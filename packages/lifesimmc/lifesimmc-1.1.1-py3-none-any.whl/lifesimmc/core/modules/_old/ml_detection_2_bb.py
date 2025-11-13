import sys

import numpy as np
import sympy as sp
import torch
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm
from phringe.api import PHRINGE
from phringe.util.spectrum import create_blackbody_spectrum
from scipy.stats import ncx2, norm

sys.path.append("/home/huberph/lifesimmc")
from lifesimmc.core.modules.base_module import BaseModule


class MLDetectionModule2_BB(BaseModule):
    """Module to estimate the flux using a parametric maximum likelihood estimation"""

    def __init__(self):
        """Constructor method."""
        self.fov = None
        self.wavelength = None
        self.context = None
        self.nulling_baseline = None
        self.diff_ir = None
        self._intensity_response = None
        # self.gpus = gpus

    def get_analytical_expr_counts(self):
        """Return data (counts) calculated using a parametric model."""

        t, flux, pos_x, pos_y, lam, nb, br, eta, ap, mod = sp.symbols('t flux pos_x pos_y lam nb br eta ap mod')
        # Rotation matrix
        argument = 2 * sp.pi / mod * t
        c = sp.cos(argument)
        s = sp.sin(argument)
        rotation_matrix = np.stack([
            c, -s,
            s, c
        ]).reshape(2, 2)

        # X static
        baseline_ratio = br
        x_static = nb / 2 * np.asarray(
            [[baseline_ratio, baseline_ratio, -baseline_ratio, -baseline_ratio], [1, -1, -1, 1]])

        # X rotating --> collector positions
        array_pos = rotation_matrix @ x_static

        # Complex amplitudes
        complex_amplitudes = sp.zeros(array_pos.shape[1], dtype=complex)
        for i in range(array_pos.shape[1]):
            complex_amplitudes[i] = ap / 2 * sp.sqrt(
                eta) * sp.exp(
                1j * 2 * sp.pi * (
                        array_pos[0, i] * pos_x + array_pos[1, i] * pos_y) / lam)

        # Get CATM X
        catm = 1 / 2 * np.asarray([[0, 0, sp.sqrt(2), sp.sqrt(2)],
                                   [sp.sqrt(2), sp.sqrt(2), 0, 0],
                                   [1, -1, -sp.exp(1j * sp.pi / 2),
                                    sp.exp(1j * sp.pi / 2)],
                                   [1, -1, sp.exp(1j * sp.pi / 2),
                                    -sp.exp(1j * sp.pi / 2)]])

        # Intensity response
        ir = sp.zeros(catm.shape[1])
        for j in range(catm.shape[1]):
            for k in range(catm.shape[0]):
                ir[j] += catm[j, k] * complex_amplitudes[k]
            ir[j] = sp.Abs(ir[j]) ** 2
        indices = self.context.instrument.beam_combiner.get_differential_output_pairs()
        diff_ir = ir[indices[0][0]] - ir[indices[0][1]]

        return flux * diff_ir

    def get_analytical_expr_ir(self):
        """Return the intensity response calculated using a parametric model."""

        t, flux, pos_x, pos_y, lam, nb, br, eta, ap, mod = sp.symbols('t flux pos_x pos_y lam nb br eta ap mod')
        # Rotation matrix
        argument = 2 * sp.pi / mod * t
        c = sp.cos(argument)
        s = sp.sin(argument)
        rotation_matrix = np.stack([
            c, -s,
            s, c
        ]).reshape(2, 2)

        # X static
        baseline_ratio = br
        x_static = nb / 2 * np.asarray(
            [[baseline_ratio, baseline_ratio, -baseline_ratio, -baseline_ratio], [1, -1, -1, 1]])

        # X rotating --> collector positions
        array_pos = rotation_matrix @ x_static

        # Complex amplitudes
        complex_amplitudes = sp.zeros(array_pos.shape[1], dtype=complex)
        for i in range(array_pos.shape[1]):
            complex_amplitudes[i] = ap / 2 * sp.sqrt(
                eta) * sp.exp(
                1j * 2 * sp.pi * (
                        array_pos[0, i] * pos_x + array_pos[1, i] * pos_y) / lam)

        # Get CATM X
        catm = 1 / 2 * np.asarray([[0, 0, sp.sqrt(2), sp.sqrt(2)],
                                   [sp.sqrt(2), sp.sqrt(2), 0, 0],
                                   [1, -1, -sp.exp(1j * sp.pi / 2),
                                    sp.exp(1j * sp.pi / 2)],
                                   [1, -1, sp.exp(1j * sp.pi / 2),
                                    -sp.exp(1j * sp.pi / 2)]])

        # Intensity response
        ir = sp.zeros(catm.shape[1])
        for j in range(catm.shape[1]):
            for k in range(catm.shape[0]):
                ir[j] += catm[j, k] * complex_amplitudes[k]
            ir[j] = sp.Abs(ir[j]) ** 2

        return ir

    def apply(self, context):
        """Apply module"""

        def get_model_single(time, flux, x_pos, y_pos):
            """Return the data model for a single wavelength."""

            from numpy import exp, pi, sin, cos, sqrt
            t = time
            flux = flux
            pos_x = x_pos
            pos_y = y_pos
            ap = self.context.instrument.aperture_diameter.numpy()
            eta = self.context.instrument.unperturbed_instrument_throughput.numpy()
            lam = self.wavelength
            nb = self.nulling_baseline
            br = self.context.observation.baseline_ratio
            mod = self.context.observation.modulation_period
            I = 1j

            expr = flux * (-abs(-0.25 * ap * sqrt(eta) * exp(0.5 * I * pi) * exp(2.0 * I * pi * (
                    pos_x * (-br * nb * cos(2 * pi * t / mod) / 2 - nb * sin(2 * pi * t / mod) / 2) + pos_y * (
                    -br * nb * sin(2 * pi * t / mod) / 2 + nb * cos(
                2 * pi * t / mod) / 2)) / lam) + 0.25 * ap * sqrt(eta) * exp(0.5 * I * pi) * exp(
                2.0 * I * pi * (
                        pos_x * (-br * nb * cos(2 * pi * t / mod) / 2 + nb * sin(2 * pi * t / mod) / 2) + pos_y * (
                        -br * nb * sin(2 * pi * t / mod) / 2 - nb * cos(
                    2 * pi * t / mod) / 2)) / lam) + 0.25 * ap * sqrt(eta) * exp(2.0 * I * pi * (
                    pos_x * (br * nb * cos(2 * pi * t / mod) / 2 - nb * sin(2 * pi * t / mod) / 2) + pos_y * (
                    br * nb * sin(2 * pi * t / mod) / 2 + nb * cos(
                2 * pi * t / mod) / 2)) / lam) - 0.25 * ap * sqrt(eta) * exp(2.0 * I * pi * (
                    pos_x * (br * nb * cos(2 * pi * t / mod) / 2 + nb * sin(2 * pi * t / mod) / 2) + pos_y * (
                    br * nb * sin(2 * pi * t / mod) / 2 - nb * cos(2 * pi * t / mod) / 2)) / lam)) ** 2 + abs(
                0.25 * ap * sqrt(eta) * exp(0.5 * I * pi) * exp(2.0 * I * pi * (
                        pos_x * (-br * nb * cos(2 * pi * t / mod) / 2 - nb * sin(2 * pi * t / mod) / 2) + pos_y * (
                        -br * nb * sin(2 * pi * t / mod) / 2 + nb * cos(
                    2 * pi * t / mod) / 2)) / lam) - 0.25 * ap * sqrt(eta) * exp(0.5 * I * pi) * exp(
                    2.0 * I * pi * (pos_x * (
                            -br * nb * cos(2 * pi * t / mod) / 2 + nb * sin(2 * pi * t / mod) / 2) + pos_y * (
                                            -br * nb * sin(2 * pi * t / mod) / 2 - nb * cos(
                                        2 * pi * t / mod) / 2)) / lam) + 0.25 * ap * sqrt(eta) * exp(
                    2.0 * I * pi * (pos_x * (
                            br * nb * cos(2 * pi * t / mod) / 2 - nb * sin(2 * pi * t / mod) / 2) + pos_y * (
                                            br * nb * sin(2 * pi * t / mod) / 2 + nb * cos(
                                        2 * pi * t / mod) / 2)) / lam) - 0.25 * ap * sqrt(eta) * exp(
                    2.0 * I * pi * (pos_x * (
                            br * nb * cos(2 * pi * t / mod) / 2 + nb * sin(2 * pi * t / mod) / 2) + pos_y * (
                                            br * nb * sin(2 * pi * t / mod) / 2 - nb * cos(
                                        2 * pi * t / mod) / 2)) / lam)) ** 2)
            return expr

        def get_model(time, x_pos, y_pos, t, r):
            """Return the data model for all wavelengths."""

            # first half of values of a_flux are a, second half are flux
            # a = a_flux[:len(self.time_steps)]
            # flux = flux[len(self.time_steps):]

            dit = self.dit
            wl_bin = self.wl_bin
            solid_angle = torch.pi * (r / self.star_distance) ** 2
            flux = create_blackbody_spectrum(t, torch.tensor(self.wavelengths)) * solid_angle
            # eta_t = self.eta_t
            model = np.zeros((len(self.wavelengths), len(time)))
            for i, wavelength in enumerate(self.wavelengths):
                self.wavelength = wavelength
                model[i] = get_model_single(time, flux[i], x_pos, y_pos) * wl_bin[i] * dit
            # if self.polyfits is not None:
            #     for i, t in enumerate(time):
            #         model[:, i] -= a[i] * self.polyfits[0, :, i]
            return model

        def lnlike(theta, x, y, yerr):
            posx, posy, *a_flux = theta
            model = get_model(x, posx, posy, *a_flux)
            # inv_sigma2 = 1.0 / (yerr ** 2 + model ** 2 * np.exp(2 * lnf))
            # return -0.5 * (np.sum((y - model) ** 2 * inv_sigma2 - np.log(inv_sigma2)))

            return -0.5 * np.sum(np.einsum('ij, i -> ij', (y - model) ** 2, 1 / yerr ** 2))

            # return -0.5 * np.sum(((y - model) ** 2 / yerr ** 2))

        def lnprior(theta):
            posx, posy, *a_flux = theta
            hfov = np.max(self.fovs) / 2
            # TODO: add smoothness prior
            flux = a_flux[len(a_flux) // 2:]
            if 0 <= np.asarray(flux)[:-1].all() < np.inf and -hfov < posx < hfov and -hfov < posy < hfov:
                return 0.0
            return -np.inf

        def lnprob(theta, x, y, yerr):
            lp = lnprior(theta)
            if not np.isfinite(lp):
                return -np.inf
            return lp + lnlike(theta, x, y, yerr)

        # Definitions
        #########################################################################
        # Working

        # Generate data
        phringe = PHRINGE()

        settings = context.simulation
        settings.has_planet_signal = False

        phringe.run(
            config_file_path=context.configuration,
            exoplanetary_system_file_path=context.exoplanetary_system_file_path,
            settings=settings,
            observatory=context.instrument,
            observation=context.observation,
            scene=context.scene,
            spectrum_files=context.spectrum_files,
            gpus=None,
            output_dir='',
            write_fits=False,
            create_copy=False,
            detailed=False
        )

        # Extract data from PHRINGE
        self._intensity_response = phringe.get_intensity_response()
        # self.diff_ir = (self._intensity_response['Earth'][:, 2, :, :, :] - self._intensity_response['Earth'][:, 3, :, :,
        #                                                                    :]).numpy().astype(np.float64)
        self.nulling_baseline = phringe._director.nulling_baseline  # phringe.get_nulling_baseline()
        self.context = context
        # wavelength_index = 10
        self.wavelengths = phringe.get_wavelength_bin_centers().numpy()
        # self.wavelength = phringe.get_wavelength_bin_centers().numpy()[wavelength_index]
        # self.fov = phringe.get_field_of_view()[wavelength_index] * 10
        self.fovs = phringe.get_field_of_view().numpy() * 10
        self.dit = phringe._director._detector_integration_time
        self.wl_bin = phringe._director._instrument_wavelength_bin_widths.cpu().numpy()
        self.eta_t = phringe._director._unperturbed_instrument_throughput.cpu().numpy()
        # self.polyfits = context.polyfits.numpy()
        flux_real = (np.float64(phringe._director._planets[0].spectral_flux_density.cpu().numpy())).tolist()
        # flux_init = [1e5] * len(flux_real)

        xdata = phringe.get_time_steps().numpy()
        self.time_steps = xdata
        ydata = context.data[0].numpy().astype(np.float64)
        original_data = np.copy(ydata)
        self.star_distance = phringe._director._star.distance
        solid_angle = torch.pi * (6e6 / self.star_distance) ** 2

        flux_init = create_blackbody_spectrum(288, torch.tensor(self.wavelengths)).numpy() * solid_angle

        # plt.imshow(ydata, cmap='Greys')
        # plt.colorbar()
        # plt.title('Original Data')
        # plt.show()

        # # Get analytical expression
        # expr = self.get_analytical_expr()
        # print(expr)
        # expr = self.get_analytical_expr_ir()
        # print(expr)

        # covariance estimation and whitening
        #########################################################
        data_wop = phringe.get_data().numpy().astype(np.float64)[0]
        cov = np.cov(data_wop.reshape(-1, data_wop.shape[1]))

        print(np.isnan(data_wop).any())
        print(np.isnan(cov).any())

        try:
            plt.imshow(cov, cmap='Greys', norm=LogNorm())
            plt.title('Covariance Matrix')
            plt.colorbar()
            plt.show()
        except ValueError:
            plt.close()

        # plt.imshow(get_model(xdata, 3.3e-7, 3.3e-7, *flux_init), cmap='Greys')
        # plt.colorbar()
        # plt.title('Original Model')
        # plt.show()

        try:
            self.icov2 = np.linalg.inv(np.sqrt(cov))
        except np.linalg.LinAlgError:
            self.icov2 = np.nan

        # check if has any nan elements
        if not np.isnan(self.icov2).any():
            ydata = self.icov2 @ ydata
            context.i_cov_sqrt = self.icov2
            context.data[0] = torch.tensor(ydata)
            # plt.imshow(self.icov @ get_model(xdata, 3.3e-7, 3.3e-7, *flux_real), cmap='Greys')
            # plt.colorbar()
            # plt.title('Whitened Model')
            # plt.show()
        else:
            print('Covariance matrix is not invertible')

        # Flatten data
        #########################################################################
        ydataf = ydata.flatten()

        # Energy detector test
        #########################################################

        ndim = ydataf.size
        te = (ydataf @ ydataf.T) / ndim  # np.sum(ydata ** 2) / ndim
        pfa = 0.05
        xsi = ncx2.ppf(1 - pfa, df=ndim, nc=0)

        # print(ndim)
        print(te)
        print(xsi)

        # ML Fit
        #########################################################

        from lmfit import minimize, Parameters
        params = Parameters()
        posx = 3.45e-7
        posy = 3.45e-7

        # compare to blackbody
        # solid_anlge = phringe._director._planets[0].solid_angle
        # flux_init = create_blackbody_spectrum(288, torch.tensor(self.wavelengths)).numpy() * solid_anlge
        plt.plot(self.wavelengths, flux_init)
        plt.show()

        # for i in range(len(flux_real)):
        #     params.add(f'flux_{i}', value=flux_init[i], min=0, max=1e8)
        params.add('pos_x', value=posx, min=-self.fovs[0], max=self.fovs[0])
        params.add('pos_y', value=posy, min=-self.fovs[0], max=self.fovs[0])
        params.add('temp', value=300, min=0, max=1000)
        params.add('radius', value=6e6, min=0, max=1e10)

        def residual_data(params, target):
            posx = params['pos_x'].value
            posy = params['pos_y'].value
            # flux = [params[f'flux_{i}'].value for i in range(len(flux_real))]
            temp = params['temp'].value
            radius = params['radius'].value
            if np.isnan(self.icov2).any():
                model = get_model(xdata, posx, posy, temp, radius)
            else:
                model = self.icov2 @ get_model(xdata, posx, posy, temp, radius)
            return model - target

        print(np.isnan(ydata).any())
        out = minimize(residual_data, params, args=(ydata,), method='leastsq')

        # out = minimize(residual_data, params, args=ydata, method='emcee', nan_policy='omit', burn=300, steps=1000,
        #                is_weighted=True)

        # print(out.params)
        # print(out.covar)
        cov = out.covar
        if cov is not None:
            print(cov.shape)
        else:
            print('No covariance matrix')
        stds = np.sqrt(np.diag(cov))
        # print(stds)

        # # print all values and uncertainties for flux and positions
        # for i in range(len(flux_real)):
        #     print(f'Flux {i}: {out.params[f"flux_{i}"].value} +/- {stds[i]}')
        # print(f'Pos X: {out.params["pos_x"].value} +/- {stds[-2]}')
        # print(f'Pos Y: {out.params["pos_y"].value} +/- {stds[-1]}')

        # fluxes = [out.params[f'flux_{i}'].value for i in range(len(flux_real))]
        posx = out.params['pos_x'].value
        posy = out.params['pos_y'].value
        temp = out.params['temp'].value
        radius = out.params['radius'].value

        # flux_err = [stds[i] for i in range(len(flux_real))]
        posx_err = stds[-2]
        posy_err = stds[-1]
        temp_err = stds[-3]
        radius_err = stds[-4]

        # best_fit = get_model(xdata, out.params['pos_x'].value, out.params['pos_y'].value,
        #                      *[out.params[f'flux_{i}'].value for i in range(len(flux_real))])

        best_fit = get_model(xdata, posx, posy, temp, radius)

        # # Plot original data and fit in 2 3x2 grid
        # plt.subplot(3, 2, 1)
        # plt.imshow(original_data, cmap='Greys')
        # plt.colorbar()
        # plt.title('Original Data')
        #
        # plt.subplot(3, 2, 2)
        # plt.imshow(ydata, cmap='Greys')
        # plt.colorbar()
        # plt.title('Whitened Data')
        #
        # plt.subplot(3, 2, 3)
        # plt.imshow(get_model(xdata, posx, posy, *flux_init), cmap='Greys')
        # plt.colorbar()
        # plt.title('Original Model')
        #
        # plt.subplot(3, 2, 4)
        # plt.imshow(self.icov2 @ get_model(xdata, posx, posy, *flux_real), cmap='Greys')
        # plt.colorbar()
        # plt.title('Whitened Model')
        #
        # plt.subplot(3, 2, 5)
        # plt.imshow(best_fit, cmap='Greys')
        # plt.colorbar()
        # plt.title('Best Fit')
        #
        # plt.tight_layout()
        # plt.show()

        # Plot best flux and snr in a 2x1 grid
        solid_angle = torch.pi * (radius / self.star_distance) ** 2
        flux = create_blackbody_spectrum(temp, torch.tensor(self.wavelengths)).numpy() * solid_angle
        # plt.subplot(2, 1, 1)
        plt.plot(flux_real[:-1], linestyle='dashed', label='True', color='black')
        plt.plot(flux)
        # plt.errorbar(range(len(fluxes[:-1])), fluxes[:-1], yerr=flux_err[:-1], fmt='o', color='black', label='Fit')
        # plt.fill_between(
        #     range(len(flux_real[:-1])),
        #     np.array(flux_real[:-1]) - np.array(flux_err[:-1]),
        #     np.array(flux_real[:-1]) + np.array(flux_err[:-1]),
        #     color="k", alpha=0.2, label='1-$\sigma$'
        # )
        plt.legend()
        plt.ylim(0, 1e6)
        plt.show()
        print(f'radius: {radius} +/- {radius_err}')
        print(f'temp: {temp} +/- {temp_err}')

        # # snr
        # bins = phringe._director._instrument_wavelength_bin_widths.cpu().numpy()[:-1]
        # snr = fluxes / np.array(flux_err)
        # snr_total = np.round(np.sqrt(np.sum(snr ** 2)), 1)
        #
        # plt.subplot(2, 1, 2)
        # plt.step(bins, snr[:-1], where='mid')
        # plt.title(f'SNR: {snr_total}')
        #
        # plt.tight_layout()
        # plt.show()

        # Neyman-Pearson test
        #########################################################

        model = (self.icov2 @ get_model(xdata, posx, posy, temp, radius)).flatten()
        xtx = (model.T.dot(model)) / ndim
        pfa = 0.0001
        xsi = np.sqrt(xtx) * norm.ppf(1 - pfa)
        tnp = (ydataf.T @ model) / ndim

        print(xtx)
        print(f'xsi: {xsi}')
        print(f'tnp: {tnp}')

        pdet = 1 - norm.cdf((xsi - xtx) / np.sqrt(xtx), loc=0, scale=1)
        print(f'pdet: {pdet}')

        z = np.linspace(-0.5 * xtx, 4 * xsi, 1000)
        zdet = z[z > xsi]
        zndet = z[z < xsi]
        fig = plt.figure(dpi=150)
        plt.plot(z, norm.pdf(z, loc=0, scale=np.sqrt(xtx)), label=f"Pdf($T_{{NP}} | \mathcal{{H}}_0$)")
        plt.fill_between(zdet, norm.pdf(zdet, loc=0, scale=np.sqrt(xtx)), alpha=0.3,
                         label=f"$P_{{FA}}$")  # , hatch="//"
        # plt.fill_between(z[], )
        plt.plot(z, norm.pdf(z, loc=xtx, scale=np.sqrt(xtx)), label=f"Pdf($T_{{NP}}| \mathcal{{H}}_1$)")
        plt.fill_between(zdet, norm.pdf(zdet, loc=xtx, scale=np.sqrt(xtx)), alpha=0.3, label=f"$P_{{Det}}$")
        plt.axvline(xsi, color="gray", linestyle="--", label=f"$\\xi(P_{{FA}}={pfa})$")
        plt.xlabel(f"$T_{{NP}}$")
        plt.ylabel(f"$PDF(T_{{NP}})$")
        plt.legend()
        plt.show()

        return context
