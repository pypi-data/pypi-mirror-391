from copy import copy
from itertools import product
from typing import Union

import numpy as np
import torch
from numpy import kron
from phringe.core.entities.perturbations.amplitude_perturbation import AmplitudePerturbation
from phringe.core.entities.perturbations.phase_perturbation import PhasePerturbation
from phringe.core.entities.perturbations.polarization_perturbation import PolarizationPerturbation
from phringe.main import PHRINGE
from scipy.linalg import fractional_matrix_power
from tqdm import tqdm

from lifesimmc.core.modules.processing.base_transformation_module import BaseTransformationModule
from lifesimmc.core.resources.base_resource import BaseResource
from lifesimmc.core.resources.data_resource import DataResource
from lifesimmc.core.resources.template_resource import TemplateResource
from lifesimmc.core.resources.transformation_resource import TransformationResource


class SpectroTemporalWhiteningModule2(BaseTransformationModule):
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
        setup = self.get_resource_from_name(self.n_config_in) if self.n_config_in else None
        # data_cov_in = self.get_resource_from_name(self.n_data_cov_in).get_data().cpu().numpy()
        data_whiten_in = self.get_resource_from_name(self.n_data_whiten_in).get_data().cpu().numpy()

        ##

        phringe = PHRINGE(
            seed=None,
            gpu_index=self.gpu_index,
            grid_size=self.grid_size,
            time_step_size=self.time_step_size,
            device=self.device,
            extra_memory=20
        )

        # Create a copy of the instrument and add draw new perturbation time series
        inst = setup.instrument
        amplitude_pert = inst.perturbations.amplitude
        phase_pert = inst.perturbations.phase
        polarization_pert = inst.perturbations.polarization

        inst_new = copy(inst)

        if amplitude_pert.rms is not None:
            inst_new.remove_perturbation(amplitude_pert)
            amplitude_pert_new = AmplitudePerturbation(rms=amplitude_pert.rms, color_coeff=amplitude_pert.color_coeff)
            inst_new.add_perturbation(amplitude_pert_new)

        if phase_pert.rms is not None:
            inst_new.remove_perturbation(phase_pert)
            phase_pert_new = PhasePerturbation(rms=phase_pert.rms, color_coeff=phase_pert.color_coeff)
            inst_new.add_perturbation(phase_pert_new)

        if polarization_pert.rms is not None:
            inst_new.remove_perturbation(polarization_pert)
            polarization_pert_new = PolarizationPerturbation(rms=polarization_pert.rms,
                                                             color_coeff=polarization_pert.color_coeff)
            inst_new.add_perturbation(polarization_pert_new)

        phringe.set(inst_new)

        # Set the observation
        phringe.set(setup.observation)

        # Remove all planets from the scene to calculate covariance only on noise
        scene_new = copy(setup.scene)
        for i, planet in enumerate(setup.scene.planets):
            setup.scene.planets[i].radius = 0.0000001
            # scene_new.remove_source(planet.name)
        phringe.set(scene_new)

        # Get the differential counts for the calibration star
        data_cov_in = phringe.get_diff_counts().cpu().numpy()
        ##

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

            from sklearn.linear_model import LinearRegression

            # Example data (replace this with your real data matrix)
            # For now, generate a dummy matrix (height x width)
            height, width = counts.shape
            # Simulate stripes with a polynomial + noise
            data = counts_ref

            # Step 1: Fit a 3rd-order poly to each column
            poly_coeffs = []
            top_values = []

            for j in range(data.shape[1]):
                y = data[:, j]
                p = np.polyfit(x, y, 3)
                poly_coeffs.append(p)
                top_values.append(y[0])  # or use p[-1] = y(x=0) = d

            poly_coeffs = np.array(poly_coeffs)
            top_values = np.array(top_values).reshape(-1, 1)

            # Step 2: Fit regression models for each coefficient
            regressors = []
            for j in range(4):
                model = LinearRegression().fit(top_values, poly_coeffs[:, j])
                regressors.append(model)

            # Step 3: Predict stripe given top value (e.g., 400)
            def predict_stripe(top_value, x=x):
                top_value = np.array([[top_value]])
                coeffs = [reg.predict(top_value)[0] for reg in regressors]
                return np.polyval(coeffs, x)

            # Plot a few examples
            for val in [-400, 0, 400]:
                stripe = predict_stripe(val)
            #     plt.plot(stripe, label=f"Top = {val}")
            # plt.legend()
            # plt.title("Predicted stripes")
            # plt.xlabel("Row index")
            # plt.ylabel("Value")
            # plt.show()

            # Generate high sample calibration data
            for j in range(data.shape[1]):
                counts_cal[:, j] = predict_stripe(calibration[j], x=wavelengths_cal)

            # plt.imshow(counts_cal, cmap='viridis', aspect='auto')
            # plt.title('Calibration Counts')
            # plt.colorbar()
            # plt.show()

            cov_t = np.cov(counts_cal.T)
            ###
            cov_w = np.cov(data_cov_in[i])

            # Covariance matrices
            U, S, Vh = np.linalg.svd(cov_t)
            W_t = U @ np.diag(1.0 / np.sqrt(S)) @ U.T

            W_l = fractional_matrix_power(cov_w, -0.5)

            var_white = np.trace(W_t @ W_t.T) / W_t.shape[0]  # average variance per time bin
            scale_factor = 1.0 / np.sqrt(var_white)
            W_t *= scale_factor

            i_cov_sqrt[i] = kron(W_t, W_l)
            #
            # test = torch.var(i_cov_sqrt[i] @ data_cov_in[i].t().reshape(1, -1)[0])
            # i_cov_sqrt[i] = i_cov_sqrt[i] / torch.sqrt(test)

            data = data_whiten_in[i].T.reshape(1, -1)[0]

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
            data_whiten_in[i] = data_white
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
