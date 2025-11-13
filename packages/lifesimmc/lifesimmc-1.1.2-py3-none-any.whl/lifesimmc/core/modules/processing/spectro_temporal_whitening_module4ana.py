from copy import copy
from itertools import product
from typing import Union

import torch
from numpy import kron
from scipy.linalg import fractional_matrix_power
from tqdm import tqdm

from lifesimmc.core.modules.processing.base_transformation_module import BaseTransformationModule
from lifesimmc.core.resources.base_resource import BaseResource
from lifesimmc.core.resources.data_resource import DataResource
from lifesimmc.core.resources.template_resource import TemplateResource
from lifesimmc.core.resources.transformation_resource import TransformationResource


class SpectroTemporalWhiteningModule4(BaseTransformationModule):
    """Class representation of the ZCA whitening transformation module. This module applied ZCA whitening to the data
    and templates using a covariance matrix based on a calibration star. The properties of this calibration star are
    assumed to be identical to the properties of the target star.

    Parameters
    ----------

    n_setup_in : str
        Name of the input configuration resource.
    n_data_cov_in : str
        Name of the input data resource.
    n_template_in : str
        Name of the input template resource.
    n_data_out : str
        Name of the output data resource.
    n_template_out : str
        Name of the output template resource.
    n_transformation_out : str
        Name of the output transformation resource.
    diagonal_only : bool
        If True, only the diagonal of the covariance matrix is used for whitening. Default is False.
    """

    def __init__(
            self,
            n_setup_in: str,
            n_data_cov_in: str,
            n_data_whiten_in: str,
            n_data_out: str,
            n_transformation_out: str,
            n_template_in: str = None,
            n_template_out: str = None,
            diagonal_only: bool = False
    ):
        """Constructor method.

        Parameters
        ----------
        n_setup_in : str
            Name of the input configuration resource.
        n_data_cov_in : str
            Name of the input data resource.
        n_template_in : str
            Name of the input template resource.
        n_data_out : str
            Name of the output data resource.
        n_template_out : str
            Name of the output template resource.
        n_transformation_out : str
            Name of the output transformation resource.
        diagonal_only : bool
            If True, only the diagonal of the covariance matrix is used for whitening. Default is False.
        """
        super().__init__()
        self.n_config_in = n_setup_in
        self.n_data_cov_in = n_data_cov_in
        self.n_data_whiten_in = n_data_whiten_in
        self.n_template_in = n_template_in
        self.n_data_out = n_data_out
        self.n_template_out = n_template_out
        self.n_transformation_out = n_transformation_out
        self.diagonal_only = diagonal_only

    def apply(self, resources: list[BaseResource]) -> Union[
        tuple[DataResource, TemplateResource, TransformationResource], tuple[DataResource, TransformationResource]]:
        """Apply the module.

        Parameters
        ----------
        resources : list[BaseResource]
            List of resources to be processed.

        Returns
        -------
        tuple[DataResource, TemplateResource, TransformationResource]
            Tuple containing the output data resource, template resource, and transformation resource.
        """
        print('Applying ZCA whitening...')

        import numpy as np

        def linear_conv_freq_same(A, B, dim=-1, one_sided=False, keep_real=False):
            """
            Linear convolution along `dim` via FFT, returned with the SAME length as inputs.

            Args:
                A, B: tensors with the same length F along `dim`.
                dim: axis of the frequency grid.
                one_sided: True if your freq grid is ω >= 0 only; False if two-sided & centred at 0.
                keep_real: if True, returns .real (otherwise complex).

            Returns:
                Tensor with the same shape as A/B (length F along `dim`).
            """
            F = A.shape[dim]
            n = 2 * F - 1

            FA = torch.fft.fft(A, n=n, dim=dim)
            FB = torch.fft.fft(B, n=n, dim=dim)
            full = torch.fft.ifft(FA * FB, dim=dim)  # length 2F-1

            # Crop to SAME length
            if one_sided:
                # keep non-negative ω part: indices [F-1 : 2F-1) → length F
                start = F - 1
            else:
                # centred crop for two-sided grid
                start = (n - F) // 2
            stop = start + F

            slicer = [slice(None)] * full.ndim
            slicer[dim] = slice(start, stop)
            out = full[tuple(slicer)]

            return out.real if keep_real else out

        # Example sanity check:
        # W = invsqrt_psd(cov_t)
        # np.allclose(W @ cov_t @ W.T, np.eye(cov_t.shape[0]), atol=1e-6, rtol=1e-6)

        setup = self.get_resource_from_name(self.n_config_in) if self.n_config_in else None
        data_cov_in = self.get_resource_from_name(self.n_data_cov_in).get_data()
        data_whiten_in = self.get_resource_from_name(self.n_data_whiten_in).get_data().cpu().numpy()

        nw = data_cov_in.shape[1]
        nt = data_cov_in.shape[2]

        # cov = torch.zeros((data_cov_in.shape[0], nw * nt, nw * nt), device=self.device, dtype=torch.float32)
        i_cov_sqrt = np.zeros((data_cov_in.shape[0], nw * nt, nw * nt))

        r_data_out = DataResource(self.n_data_out)

        # Whiten data
        for i in range(len(data_cov_in)):
            calibration = data_cov_in[i, 0]

            #
            # x = calibration
            # r = x
            # r = r - np.mean(r)
            # r = r / np.std(r)
            # acf = np.correlate(r, r, mode='full')[len(r) - 1:] / len(r)
            #
            # cov_t = toeplitz(acf)

            ###
            counts = data_whiten_in[i]
            counts_ref = copy(data_cov_in[i])
            wavelengths = setup.phringe.get_wavelength_bin_centers().cpu().numpy()

            counts_cal = np.zeros((counts.shape[1] * 100, counts.shape[1]))
            wavelengths_cal = np.linspace(wavelengths[0], wavelengths[-1], counts_cal.shape[0])
            x = wavelengths
            # cov_w = np.cov(data_cov_in[i].cpu().numpy())

            ###

            nw = counts.shape[0]
            nt = counts.shape[1]
            times = setup.phringe.get_time_steps().cpu().numpy()
            dt = times[1] - times[0]
            kappa = 2
            nt = counts.shape[1]
            nl = counts.shape[0]
            wavelengths = setup.phringe.get_wavelength_bin_centers()
            counts_cal = np.zeros((counts.shape[1], counts.shape[1]))
            wavelengths_cal = np.linspace(wavelengths[0].cpu().numpy(), wavelengths[-1].cpu().numpy(),
                                          counts_cal.shape[0])
            x = wavelengths
            # data = counts_ref.cpu().numpy()

            # Get spectral covariance
            cov_w = torch.cov(counts_ref).cpu().numpy()

            # PSD
            modulation_period = setup.phringe._observation.modulation_period
            coords_star = setup.phringe._scene.star._sky_coordinates
            times = setup.phringe.get_time_steps()
            # wavelengths = phringe.get_wavelength_bin_centers()
            nulling_baseline = setup.phringe.get_nulling_baseline()
            amplitude = setup.phringe._instrument._get_amplitude(self.device)
            sky_coordinates_x = coords_star[0][None, None, :, :]
            sky_coordinates_y = coords_star[1][None, None, :, :]
            i_star = setup.phringe._scene.star._sky_brightness_distribution
            eta_qe = setup.phringe._instrument.quantum_efficiency
            wavelength_bin_widths = setup.phringe.get_wavelength_bin_widths()
            t_dit = setup.phringe._observation.detector_integration_time

            # Two sided
            nt = times.numel()
            dt = (times[1] - times[0]).item()
            omega = 2 * np.pi * torch.fft.fftshift(torch.fft.fftfreq(nt, d=dt)).to(self.device)  # shape (nt,)
            domega = float(omega[1] - omega[0])
            psd = (1.0 / torch.clamp(omega.abs(), min=2 * np.pi / (nt * dt))) ** 1  # ∝ 1/|ω|
            sda = psd.repeat(4, 1)  # [K, F]
            sdphi = psd.repeat(4, 1)
            sdtheta = psd.repeat(4, 1)

            ########################################################################################################################
            # Get basic PSD building blocks
            ########################################################################################################################
            swjx_func, swjy_func, tilde_swjy_func, wjx_func, wjy_func, c_func, vjkx_func, vjky_func, swjx_cross_func, swjy_cross_func, tilde_swjy_cross_func = setup.phringe._instrument._get_lambdified_psd()

            swjx = swjx_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
                # *[da[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dphi[k][:, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dth[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sda[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sdphi[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
            )

            swjy = swjy_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
                # *[da[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dphi[k][:, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dth[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sdtheta[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
            )

            tilde_swjy = tilde_swjy_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
                # *[da[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dphi[k][:, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dth[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sdtheta[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
            )

            wjx = wjx_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
                # *[da[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dphi[k][:, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dth[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sda[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sdphi[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
            )

            wjy = wjy_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
                # *[da[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dphi[k][:, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dth[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sdtheta[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
            )

            c = c_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
            )

            vjkx = vjkx_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
                # *[da[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dphi[k][:, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dth[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sda[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sdphi[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
            )

            vjky = vjky_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
                # *[da[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dphi[k][:, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dth[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sdtheta[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
            )

            swjx_cross = swjx_cross_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
                # *[da[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dphi[k][:, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dth[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sda[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sdphi[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
            )

            swjy_cross = swjy_cross_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
                # *[da[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dphi[k][:, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dth[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sdtheta[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
            )

            tilde_swjy_cross = tilde_swjy_cross_func(
                times[None, :, None, None],
                wavelengths[:, None, None, None],
                sky_coordinates_x,
                sky_coordinates_y,
                torch.tensor(setup.phringe._observation.modulation_period, device=self.device),
                torch.tensor(setup.phringe._instrument._nulling_baseline, device=self.device),
                *[amplitude for _ in range(setup.phringe._instrument.number_of_inputs)],
                # *[da[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dphi[k][:, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                # *[dth[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
                *[sdtheta[k][None, :, None, None] for k in range(setup.phringe._instrument.number_of_inputs)],
            )
            ########################################################################################################################
            # Check if C is constant
            ########################################################################################################################
            # print(c[0].shape)
            #
            # c1 = c[0][0, :, 0, 0].cpu().numpy()
            #
            # print(c1)
            #
            # plt.plot(c1.real)
            # plt.plot(c1.imag)
            # plt.show()
            #
            # plt.plot(abs(c1) ** 2)
            # plt.show()
            #

            ########################################################################################################################
            # Get Srjx/Srjy
            ########################################################################################################################
            conv_s_tilde_wjx = {}
            conv_s_tilde_wjy = {}
            conv_swjx = {}
            conv_swjy = {}
            srjx = {}
            srjy = {}

            for j in range(setup.phringe._instrument.number_of_outputs):
                conv_swjx[j] = domega * linear_conv_freq_same(swjx[j], torch.conj(swjx[j]), dim=1)
                conv_swjy[j] = domega * linear_conv_freq_same(swjy[j], torch.conj(swjy[j]), dim=1)
                conv_s_tilde_wjy[j] = domega * linear_conv_freq_same(tilde_swjy[j], torch.flip(tilde_swjy[j], dims=[1]),
                                                                     dim=1)

                # conv_s_tilde_wjx[j] = 0# convolve_same(s_tilde_wjx[j], torch.flip(s_tilde_wjx[j], dims=[1]), dim=1)

                # conv_swjx[j] = convolve_same(swjx[j], swjx[j], dim=1)
                # conv_swjy[j] = convolve_same(swjy[j], swjy[j], dim=1)
                # conv_s_tilde_wjy[j] = convolve_same(tilde_swjy[j], torch.flip(tilde_swjy[j], dims=[1]), dim=1,
                #                                     )

                mux = torch.mean(wjx[j], dim=1)[:, None]
                muy = 0  # torch.mean(wjy[j], dim=1)[:, None]

                srjx[j] = conv_swjx[j] + 2 * abs(mux) ** 2 * swjx[j]  # + conv_s_tilde_wjx[j]
                srjy[j] = conv_swjy[j] + 2 * abs(muy) ** 2 * swjy[j] + conv_s_tilde_wjy[j]

            ########################################################################################################################
            # Get Srjrhx/y or srrmx/y cross terms
            ########################################################################################################################
            # srrm = {}
            # srjrhx = {}
            # srjrhy = {}
            #
            # for m in range(len(setup.phringe._instrument.differential_outputs)):
            #     j, h = phringe._instrument.differential_outputs[m]
            #
            #     # srrmx = convolve_same(swjx[j], swjx[h], dim=1)
            #     # srrmy = convolve_same(swjy[j], swjy[h], dim=1)
            #     # tilde_srrmy = convolve_same(tilde_swjy[j], tilde_swjy[h], dim=1)
            #
            #     conv_swjwhx = domega * linear_conv_freq_same(swjx[j], swjx[h], dim=1)
            #     conv_swjwhy = domega * linear_conv_freq_same(swjy[j], swjy[h], dim=1)
            #     cnov_s_tilde_wjwhy = domega * linear_conv_freq_same(tilde_swjy[j], torch.flip(tilde_swjy[h], dims=[1]), dim=1)
            #
            #     # srrm[m] = srrmx + srrmy + tilde_srrmy
            #     # srrm[m] = -2 * torch.real(s_rjrh_x + s_rjrh_y) - 2 * torch.real(s_tilde_rjrh_y)
            #     srjrhx[m] = conv_swjwhx
            #     srjrhy[m] = conv_swjwhy + cnov_s_tilde_wjwhy
            #     # srrm[m] = -2 * torch.real(conv_swjwhx + conv_swjwhy + cnov_s_tilde_wjwhy)

            srrm = {}
            for m, (j, h) in enumerate(setup.phringe._instrument.differential_outputs):
                # field cross-spectra:
                Sx_jh = swjx_cross[(j, h)]
                Sy_jh = swjy_cross[(j, h)]
                tSy_jh = tilde_swjy_cross[(j, h)]

                # intensity cross-PSD per ξ:
                #   (S_{WjWh} * S_{WjWh})(ω)  and  (Ṡ_{WjWh}(ω) * Ṡ_{WjWh}(-ω))(ω)
                S_RjRh_x = domega * linear_conv_freq_same(Sx_jh, torch.conj(Sx_jh), dim=1, one_sided=False)
                S_RjRh_y = domega * linear_conv_freq_same(Sy_jh, torch.conj(Sy_jh), dim=1, one_sided=False)
                S_RjRh_t = domega * linear_conv_freq_same(tSy_jh, torch.flip(tSy_jh, dims=[1]), dim=1, one_sided=False)

                S_RjRh = S_RjRh_x + S_RjRh_y + S_RjRh_t

                # contribution to ΔR_m
                srrm[m] = -2 * torch.real(S_RjRh)
            ########################################################################################################################
            # Get Srj and the cross terms
            ########################################################################################################################
            srj = {}
            srjrh = {}

            for j in range(setup.phringe._instrument.number_of_outputs):
                srj[j] = srjx[j] + srjy[j]

            # for m in range(len(setup.phringe._instrument.differential_outputs)):
            #     srjrh[m] = srjrhx[m] + srjrhy[m]

            ########################################################################################################################
            # Get S Delta R m
            ########################################################################################################################
            sdrm = {}

            for m in range(len(setup.phringe._instrument.differential_outputs)):
                j, h = setup.phringe._instrument.differential_outputs[m]
                sdrm[m] = srj[j] + srj[h] + srrm[m]  # - 2 * srjrh[m]  # + srrm[m]  # - 2 * srrm[m].real

            # plt.plot((srj[2] + srj[3]).cpu().numpy()[0, :, 0, 0])
            # plt.plot((srm[0]).cpu().numpy()[0, :, 0, 0])
            # plt.show()

            ########################################################################################################################
            # Get Sdnm
            ########################################################################################################################

            # Calculate final PSD of counts
            i_star2 = torch.abs(i_star) ** 2

            sdr0 = sdrm[0]
            # sr = sr[0]
            sdr0 = sdr0.to(torch.float64)
            i_star2 = i_star2.to(torch.float64)

            product1 = sdr0 * i_star2[:, None, :, :]

            sdn = torch.sum(product1, dim=(-1, -2)) * abs(eta_qe * t_dit * wavelength_bin_widths[:, None]) ** 2

            # Remove DC term
            # sn[:, 0] = 0

            # plt.plot(sdn[0].cpu().numpy())
            # plt.show()
            ##

            ########################################################################################################################
            # Calculate cov using wiener-khinchin theorem
            ########################################################################################################################
            # nt = times.numel()
            dt = (times[1] - times[0]).item()  # plain float for stability

            #
            # # frequencies = omega
            # lags = torch.arange(nt, device=self.device, dtype=torch.float64)  # (nt,)
            # # phi = 2 * torch.pi * dt * (lags[:, None] * frequencies[None, :])  # (nt, K)
            # # c = 2 * (torch.cos(phi) @ sn.T) / (nt * dt)  # (nt,)
            # idx = (lags[:, None] - lags[None, :]).abs().long()  # (nt, nt)
            #
            # tau = (torch.arange(nt, device=self.device, dtype=torch.float64) * dt)  # lags in seconds
            # kernel = torch.cos(tau[:, None] * omega[None, :])  # [nt, F]
            # c = (domega / (2 * np.pi)) * (kernel @ sn.T)
            #
            # cov_t = c[idx]

            def toeplitz_from_spectrum(S_ω: torch.Tensor, dt: float, shifted: bool = True,
                                       real_output: bool = True):
                """
                Make a Toeplitz covariance matrix from a two-sided spectrum.

                Args
                ----
                S_ω : (..., N) complex tensor
                    Two-sided spectrum on an fftshift'ed ω-grid (DC in the centre).
                    For auto-covariance use the auto-PSD; for cross-covariance use the cross-spectrum.
                    If your convention needs S_xy* in the integral, pass torch.conj(S_xy) here.
                dt : float
                    Sample spacing in seconds.
                shifted : bool
                    True if S_ω is fftshift'ed (DC in the middle). Set False if it is already in DFT order.
                real_output : bool
                    If True, return real covariance (useful for auto-covariances).

                Returns
                -------
                Cov : (..., N, N) tensor
                    Toeplitz covariance matrix.
                c_lags : (..., N) tensor
                    Autocovariance / cross-covariance sequence for lags 0..N-1.
                """
                S_ω = S_ω.to(torch.complex128)

                # Put spectrum into DFT order (DC at index 0) for the IFFT
                if shifted:
                    S_unshift = torch.fft.ifftshift(S_ω, dim=-1)
                else:
                    S_unshift = S_ω

                # Continuous-time scaling for ω-grid from fftfreq: c[τ] = (1/dt) * IFFT{S(ω)}
                c_lags = (1.0 / dt) * torch.fft.ifft(S_unshift, dim=-1)

                if real_output:
                    c_lags = c_lags.real

                # Build Toeplitz: Cov[i,j] = c_lags[|i-j|]
                N = S_ω.shape[-1]
                idx = (torch.arange(N, device=S_ω.device)[:, None]
                       - torch.arange(N, device=S_ω.device)[None, :]).abs()
                Cov = c_lags[..., idx]  # broadcasts over leading dims

                return Cov, c_lags

            # sn[0] is your two-sided, mirror-symmetric PSD on an fftshift'ed ω-grid
            cov_t, c_lags = toeplitz_from_spectrum(sdn[0], dt=dt, shifted=True, real_output=True)

            maax = cov_t.max()
            miin = cov_t.min()

            v = max(abs(maax), abs(miin))
            #
            # plt.imshow(cov_t.cpu().numpy(), cmap="seismic", aspect='auto', vmin=-v, vmax=v)
            # plt.colorbar()
            # plt.show()

            cov_t = cov_t.cpu().numpy()

            ###

            # Covariance matrices
            # U, S, Vh = np.linalg.svd(cov_t)
            # W_t = U @ np.diag(1.0 / np.sqrt(S)) @ U.T

            # W_t = invsqrt_psd(cov_t)

            W_l = fractional_matrix_power(cov_w, -0.5)
            W_t = fractional_matrix_power(cov_t, -0.5).real

            var_white = np.trace(W_t @ W_t.T) / W_t.shape[0]  # average variance per time bin
            scale_factor = 1.0 / np.sqrt(var_white)
            W_t *= scale_factor

            # plt.imshow(W_t, cmap='viridis', aspect='auto')
            # plt.colorbar()
            # plt.show()

            i_cov_sqrt[i] = kron(W_t, W_l)
            #
            # test = torch.var(i_cov_sqrt[i] @ data_cov_in[i].t().reshape(1, -1)[0])
            # i_cov_sqrt[i] = i_cov_sqrt[i] / torch.sqrt(test)

            data = data_whiten_in[i, :, :].T.reshape(1, -1)[0]

            # for k, j in np.ndindex(nt, nt):
            #     if k == j:
            #         cov[i, k * nw:(k + 1) * nw, j * nw:(j + 1) * nw] = cov_w
            #     else:
            #         cov[i, k * nw:(k + 1) * nw, j * nw:(j + 1) * nw] = cov_w * cov_t[k, j] / torch.max(cov_w)
            #
            #     i_cov_sqrt[i, k * nw:(k + 1) * nw, j * nw:(j + 1) * nw] = torch.tensor(
            #         inv(sqrtm(cov[i, k * nw:(k + 1) * nw, j * nw:(j + 1) * nw].cpu().numpy())),
            #         device=self.device,
            #         dtype=torch.float32
            #     )

            data_white = i_cov_sqrt[i] @ data
            data_white = data_white.reshape(nt, nw).T
            data_whiten_in[i, :, :] = data_white
            print(np.var(data_white))

        r_data_out.set_data(torch.tensor(data_whiten_in, device=self.device, dtype=torch.float32))

        # Whiten templates if given
        if self.n_template_in and self.n_template_out:

            r_template_in = self.get_resource_from_name(self.n_template_in)
            template_data_in = r_template_in.get_data().cpu().numpy()
            template_counts_white = torch.zeros(template_data_in.shape, device=self.device, dtype=torch.float32)

            for i, j in tqdm(
                    product(range(template_data_in.shape[-2]), range(template_data_in.shape[-1])),
                    total=template_data_in.shape[-2] * template_data_in.shape[-1]
            ):
                for k in range(template_data_in.shape[0]):
                    template_counts_white[k, :, :, i, j] = torch.tensor(
                        (
                                i_cov_sqrt[k] @ template_data_in[k, :, :, i, j].T.reshape(1, -1)[0])
                        .reshape(nt, nw).T,
                        device=self.device,
                        dtype=torch.float32
                    )
                    # plt.imshow(template_counts_white[k, :, :, i, j].cpu().numpy(), cmap='bwr', aspect='auto')
                    # plt.colorbar()
                    # plt.show()

            r_template_out = TemplateResource(
                name=self.n_template_out,
                grid_coordinates=r_template_in.grid_coordinates
            )
            r_template_out.set_data(template_counts_white)
        else:
            r_template_out = None

        # Save the whitening transformation
        def zca_whitening_transformation(data):
            """Apply the ZCA whitening transformation."""
            if isinstance(data, np.ndarray):
                try:
                    i2 = i_cov_sqrt.cpu().numpy()
                except AttributeError:
                    i2 = i_cov_sqrt
            else:
                i2 = i_cov_sqrt
            for l in range(data.shape[0]):
                data[l] = (i2[l] @ data[l].T.reshape(1, -1)[0]).reshape(nt, nw).T
            return data

        zca = zca_whitening_transformation

        r_transformation_out = TransformationResource(
            name=self.n_transformation_out,
            transformation=zca
        )

        print('Done')
        if r_template_out is not None:
            return r_data_out, r_template_out, r_transformation_out
        return r_data_out, r_transformation_out
