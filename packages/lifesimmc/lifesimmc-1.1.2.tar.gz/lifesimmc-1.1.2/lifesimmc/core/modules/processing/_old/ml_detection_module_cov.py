from itertools import product
from typing import Tuple

import numpy as np
import sympy as sp
import torch
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm
from phringe.api import PHRINGE
from scipy.stats import norm
from torch import Tensor

from lifesimmc.core.modules.base_module import BaseModule
from lifesimmc.util.grid import get_indices_of_maximum_of_2d_array
from lifesimmc.util.helpers import Extraction


class MLDetectionModuleCov(BaseModule):
    """Class representation of the Maximum Likelihood extraction module."""

    def _calculate_maximum_likelihood(self, data, context, is_white=False) -> Tuple:
        """Calculate the maximum likelihood estimate for the flux in units of photons at the position of the maximum of
        the cost function.

        :param context: The context object of the pipeline
        :return: The cost function and the optimum flux
        """

        cost_function = torch.zeros(
            (
                context.instrument.beam_combiner.number_of_differential_outputs,
                context.simulation.grid_size,
                context.simulation.grid_size,
                len(context.instrument.wavelength_bin_centers)
            )
        )
        optimum_flux = torch.zeros(cost_function.shape)
        tnp = torch.zeros((context.simulation.grid_size, context.simulation.grid_size))
        # print((context.settings.grid_size, context.settings.grid_size))

        for index_x, index_y in product(range(context.simulation.grid_size), range(context.simulation.grid_size)):

            # For the data (not whitened) and if polyfit subtraction has been done, then use the templates_subtracted
            # if context.templates_subtracted is not None:
            #     # print('polyfit')
            #     template = [template for template in context.templates_subtracted if template.x == index_x and
            #                 template.y == index_y][0]
            # # For the whitened data or if no polyfit subtraction has been done, then use the original templates
            # else:
            # print('no polyfit')
            template = \
                [template for template in context.templates if template.x == index_x and template.y == index_y][
                    0]

            template_data = torch.einsum('ijk, ij->ijk', template.data,
                                         1 / torch.sqrt(torch.mean(template.data ** 2, axis=2)))

            # Whiten the template data
            # replace nan values with 0
            template_data = torch.nan_to_num(template_data, 0)

            template_data[:] = torch.tensor(self.icov2.astype(np.float32)) @ template_data[:]

            matrix_c = self._get_matrix_c(data, template_data)
            matrix_b = self._get_matrix_b(data, template_data)

            for index_output in range(len(matrix_b)):
                matrix_b = torch.nan_to_num(matrix_b, 1)  # really 1?
                optimum_flux[index_output, index_x, index_y] = torch.diag(
                    torch.linalg.inv(matrix_b[index_output]) * matrix_c[index_output])

                # Set positivity constraint
                if not is_white:
                    optimum_flux[index_output, index_x, index_y] = torch.where(
                        optimum_flux[index_output, index_x, index_y] >= 0,
                        optimum_flux[index_output, index_x, index_y],
                        0
                    )

                # Calculate the cost function according to equation B.8
                cost_function[index_output, index_x, index_y] = (optimum_flux[index_output, index_x, index_y] *
                                                                 matrix_c[index_output])

            # Neyman-Pearson test
            ########################################
            y = context.data[0].flatten()
            ndim = y.cpu().numpy().size

            # model = optimum_flux[
            #             0, index_x, index_y] @ template_data.flatten()
            # model = torch.einsum('j, ijk -> ijk', optimum_flux[0, index_x, index_y], template_data).flatten()
            model = torch.einsum('j, ijk -> ijk', self.flux_real, template_data).flatten()

            # (self.icov2 @ get_model(xdata, posx, posy, *flux_real)).flatten()
            xtx = (model.T.dot(model)) / ndim
            pfa = 0.05
            xsi = np.sqrt(xtx) * norm.ppf(1 - pfa)
            tnp[index_x, index_y] = (y.T @ model) / xsi / ndim
            # print(tnp[index_x, index_y], xsi)

            ########################################

        # Sum cost function over all wavelengths
        cost_function = torch.sum(torch.nan_to_num(cost_function, 0), axis=3)
        # cost_function[torch.isnan(cost_function)] = 0
        return cost_function, optimum_flux, tnp

    def _get_fluxes_uncertainties(self, cost_functions, cost_functions_white, optimum_fluxes_white,
                                  context) -> Tensor:
        """Return the uncertainties on the extracted fluxes by calculating the standard deviation of the extracted
        fluxes at positions around the center at a radius of the maximum cost function.

        :param cost_functions: The cost functions
        :param cost_functions_white: The whitened cost functions
        :param optimum_fluxes_white: The whitened optimum fluxes
        :param context: The context object of the pipeline
        :return: The uncertainties on the extracted fluxes
        """
        for index_output in range(len(cost_functions_white)):
            # Get extracted flux at positions around center at radius of maximum cost function
            height, width = cost_functions_white[index_output, :, :].shape
            index_max_x, index_max_y = get_indices_of_maximum_of_2d_array(cost_functions[index_output])

            # Create mask for circle around maximum of cost function
            center = (width // 2, height // 2)
            radius = torch.sqrt((index_max_x - width // 2) ** 2 + (index_max_y - width // 2) ** 2)

            width_linspace = torch.linspace(torch.asarray(0), torch.asarray(width - 1), width)
            height_linspace = torch.linspace(torch.asarray(0), torch.asarray(height - 1), height)
            y, x = torch.meshgrid(height_linspace, width_linspace)
            # y, x = torch.ogrid[:height, :width]
            mask = ((x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius ** 2 + 0.5) & \
                   ((x - center[0]) ** 2 + (y - center[1]) ** 2 >= (radius - 1) ** 2 + 0.5)

            # remove planet position from mask
            # plt.imshow(mask)
            # plt.show()

            #################
            # get array of cost function values for each pixel in the mask for each output index
            cost_function_values_in_mask = torch.zeros(
                (context.instrument.beam_combiner.number_of_differential_outputs, mask.sum()),
                dtype=torch.float32
            )
            for index_output in range(context.instrument.beam_combiner.number_of_differential_outputs):
                cost_function_values_in_mask[index_output] = cost_functions_white[index_output, :, :][mask]

            a = 0

            ################

            masked_fluxes_white_flattened = torch.einsum(
                'ijk, ij -> ijk',
                optimum_fluxes_white[index_output, :, :],
                mask
            ).reshape(context.simulation.grid_size ** 2, -1)

            uncertainties = torch.zeros(masked_fluxes_white_flattened.shape[1], dtype=torch.float32)

            for index in range(masked_fluxes_white_flattened.shape[1]):
                # Remove zero values from array, since they are not part of the mask and would change the standard
                # deviation
                non_zero_values = [el for el in masked_fluxes_white_flattened[:, index] if el > 0]
                uncertainties[index] = torch.std(torch.asarray(non_zero_values))
        return 0, cost_function_values_in_mask

    def _get_matrix_b(self, data: Tensor, template_data: Tensor) -> Tensor:
        """Calculate the matrix B according to equation B.3.

        :param data: The data
        :param template_data: The template data
        :return: The matrix B
        """
        # data_variance = torch.var(torch.tensor(self.data_wop.astype(np.float32)), axis=1)
        data_variance = torch.var(data, axis=2)
        matrix_b_elements = torch.sum(template_data ** 2, axis=2) / data_variance
        matrix_b = torch.zeros(
            matrix_b_elements.shape[0],
            matrix_b_elements.shape[1],
            matrix_b_elements.shape[1],
            dtype=torch.float32
        )
        for index_output in range(len(matrix_b_elements)):
            matrix_b[index_output] = torch.diag(matrix_b_elements[index_output])

        return matrix_b

    def _get_matrix_c(self, data: Tensor, template_data: Tensor) -> Tensor:
        """Calculate the matrix C according to equation B.2.

        :param signal: The signal
        :param template_signal: The template signal
        :return: The matrix C
        """
        # data_variance = torch.var(torch.tensor(self.data_wop.astype(np.float32)), axis=1)
        data_variance = torch.var(data, axis=2)
        return torch.sum(data * template_data, axis=2) / data_variance

    def _get_optimum_flux_at_cost_function_maximum(self, cost_functions, optimum_fluxes, context) -> Tensor:
        """Calculate the optimum flux at the position of the maximum of the cost function.

        :param cost_functions: The cost functions
        :param optimum_fluxes: The optimum fluxes
        :param context: The context object of the pipeline
        :return: The optimum flux at the position of the maximum of the cost function
        """
        optimum_flux_at_maximum = torch.zeros(
            (
                context.instrument.beam_combiner.number_of_differential_outputs,
                len(context.instrument.wavelength_bin_centers)
            ),
            dtype=torch.float32
        )

        for index_output in range(len(optimum_flux_at_maximum)):
            index_x, index_y = get_indices_of_maximum_of_2d_array(cost_functions[index_output])
            optimum_flux_at_maximum[index_output] = optimum_fluxes[index_output, index_x, index_y]

        return optimum_flux_at_maximum

    def _get_whitened_data(self, optimum_fluxes, cost_functions, context) -> Tensor:
        """Return the whitened signal, i.e. the original signal with the most likely planet signal substracted.

        :param optimum_fluxes: The optimum fluxes
        :param cost_functions: The cost functions
        :param context: The context object of the pipeline
        :return: The whitened signal
        """
        for index_output in range(context.instrument.beam_combiner.number_of_differential_outputs):
            index_x, index_y = get_indices_of_maximum_of_2d_array(cost_functions[index_output])
            print(index_x, index_y)
            signal_white = context.data.detach().clone()
            # Always use original templates for whitening
            template = \
                [template for template in context.templates if template.x == index_x and template.y == index_y][
                    0]
            signal_white -= torch.einsum(
                'ij, ijk->ijk',
                optimum_fluxes[:, index_x, index_y],
                template.data
            )
        return signal_white

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
        """Apply the module.

        :param context: The context object of the pipelines
        :return: The (updated) context object
        """

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
            br = self.context.observation_mode.baseline_ratio
            mod = self.context.observation_mode.modulation_period
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

        def get_model(time, x_pos, y_pos, *flux):
            """Return the data model for all wavelengths."""

            # first half of values of a_flux are a, second half are flux
            # a = a_flux[:len(self.time_steps)]
            # flux = flux[len(self.time_steps):]

            dit = self.dit
            wl_bin = self.wl_bin
            # eta_t = self.eta_t
            model = np.zeros((len(self.wavelengths), len(time)))
            for i, wavelength in enumerate(self.wavelengths):
                self.wavelength = wavelength
                model[i] = get_model_single(time, flux[i], x_pos, y_pos) * wl_bin[i] * dit
            # if self.polyfits is not None:
            #     for i, t in enumerate(time):
            #         model[:, i] -= a[i] * self.polyfits[0, :, i]
            return model

        #################################################

        # Generate empty data for covariance estimation
        phringe = PHRINGE()

        settings = context.simulation
        settings.has_planet_signal = False

        phringe.run(
            config_file_path=context.config_file_path,
            exoplanetary_system_file_path=context.exoplanetary_system_file_path,
            settings=settings,
            observatory=context.instrument,
            observation=context.observation_mode,
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
        self.flux_real = (np.float64(phringe._director._planets[0].spectral_flux_density.cpu().numpy())).tolist() if \
            phringe._director._planets[0].spectral_flux_density is not None else None
        # flux_init = [1e5] * len(flux_real)
        xdata = phringe.get_time_steps().numpy()
        self.time_steps = xdata
        ydata = context.data[0].numpy().astype(np.float64)
        original_data = np.copy(ydata)

        # Generate templates grid
        #########################################################
        grid = 10
        x_pos = np.linspace(-self.fovs[0], self.fovs[0], grid)
        y_pos = np.linspace(-self.fovs[0], self.fovs[0], grid)
        # x_pos, y_pos = np.meshgrid(x_pos, y_pos)

        # covariance estimation and whitening
        #########################################################
        self.data_wop = phringe.get_data().numpy().astype(np.float64)[0]
        cov = np.cov(self.data_wop.reshape(-1, self.data_wop.shape[1]))

        print(np.isnan(self.data_wop).any())
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
            context.icov2 = self.icov2
            context.data[0] = torch.tensor(ydata)
            # self.data_wop = self.icov2 @ self.data_wop
            print('Whitening successful')
            # plt.imshow(self.icov @ get_model(xdata, 3.3e-7, 3.3e-7, *flux_real), cmap='Greys')
            # plt.colorbar()
            # plt.title('Whitened Model')
            # plt.show()
        else:
            print('Covariance matrix is not invertible')

        #########################################################

        # Get cost functions and optimum fluxes for all positions and differential outputs
        cost_functions, optimum_fluxes, tnp = self._calculate_maximum_likelihood(context.data, context)

        plt.imshow(tnp, cmap='bwr')
        plt.colorbar()
        plt.title('TNP')
        plt.show()

        plt.imshow(tnp, cmap='inferno')
        plt.colorbar()
        plt.title('TNP')
        plt.show()

        # Get the optimum flux at the position of the maximum of the cost function
        optimum_flux_at_maximum = self._get_optimum_flux_at_cost_function_maximum(
            cost_functions,
            optimum_fluxes,
            context
        )

        # # Get the whitened data and the uncertainties on the extracted flux
        # data_white = self._get_whitened_data(optimum_fluxes, cost_functions, context)
        # cost_functions_white, optimum_fluxes_white = self._calculate_maximum_likelihood(data_white, context,
        #                                                                                 is_white=True)
        #
        # # TODO: what about data whitening with poly subtraction?
        # optimum_fluxes_uncertainties, cost_function_values_in_mask = self._get_fluxes_uncertainties(
        #     cost_functions,
        #     cost_functions_white,
        #     optimum_fluxes_white,
        #     context
        # )

        # plt.hist(cost_function_values_in_mask[0])
        # plt.show()

        # plot cost function and cost function white next to eah other using subplots
        # plt.subplot(1, 2, 1)
        plt.imshow(cost_functions[0], cmap='inferno')
        plt.colorbar()
        plt.title('Cost Function')

        # plt.subplot(1, 2, 2)
        # plt.imshow(cost_functions_white[0], vmin=torch.min(cost_functions[0]),
        #            vmax=torch.max(cost_functions[0]))
        # plt.colorbar()
        # plt.title('Cost Function White')
        plt.show()

        # plot cost function and cost function white next to eah other using subplots
        # plt.subplot(1, 2, 1)
        # plt.imshow(cost_functions[0], cmap='magma')
        # plt.colorbar()
        # # plt.title('Cost Function')

        # plt.subplot(1, 2, 2)
        # plt.imshow(cost_functions_white[0], cmap='magma')
        # plt.colorbar()
        # plt.title('Cost Function White')
        # plt.savefig('image.svg')
        # plt.show()

        plt.plot(optimum_flux_at_maximum[0])
        plt.show()

        ##########
        # mu_y_hat = torch.max(cost_functions)
        # mu_x_hat = torch.mean(cost_function_values_in_mask)
        # n = len(cost_function_values_in_mask[0])
        # sigma_x_hat = torch.sqrt(torch.sum((cost_function_values_in_mask - mu_x_hat) ** 2) / (n - 1))
        # t = (mu_y_hat - mu_x_hat) / (sigma_x_hat * torch.sqrt(tensor(1 + 1 / n)))
        #
        # # calc fpf from t using t-statistics
        # fpf = scipy.stats.t.sf(t, n - 1)
        #
        # # convert fpf to sigma values
        # sigma_fpf = scipy.stats.norm.ppf(1 - fpf)
        #
        # print(mu_y_hat)
        # print(mu_x_hat)
        # print(n)
        # print(sigma_x_hat)
        # print('t: ', t)
        # print('fpf: ', fpf)
        # print('sigma: ', sigma_fpf)
        # ####

        # Neyman-Pearson test
        #########################################

        context.extractions.append(
            Extraction(
                None,
                None,
                None,
                context.instrument.wavelength_bin_centers,
                cost_functions
            )
        )

        return context
