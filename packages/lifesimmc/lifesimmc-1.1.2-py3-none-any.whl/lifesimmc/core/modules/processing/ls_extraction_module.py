import sys

import numpy as np
import sympy as sp
from matplotlib import pyplot as plt
from phringe.phringe_ui import PHRINGE

sys.path.append("/home/huberph/lifesimmc")
from lifesimmc.core.modules.base_module import BaseModule


class LSExtractionModule(BaseModule):
    """Module to estimate the flux using a parametric maximum likelihood estimation"""

    def __init__(self, gpus: tuple[int]):
        """Constructor method."""
        self.fov = None
        self.wavelength = None
        self.context = None
        self.nulling_baseline = None
        self.diff_ir = None
        self._intensity_response = None
        self.gpus = gpus

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

        def get_model_single(time, x_pos, y_pos):
            """Return the data model for a single wavelength."""

            from numpy import exp, pi, sin, cos, sqrt
            t = time
            pos_x = x_pos
            pos_y = y_pos
            ap = self.context.instrument.aperture_diameter.numpy()
            eta = self.context.instrument.unperturbed_instrument_throughput.numpy()
            lam = self.wavelength
            nb = self.nulling_baseline
            br = self.context.observation_mode.baseline_ratio
            mod = self.context.observation_mode.modulation_period
            I = 1j

            expr = (-abs(-0.25 * ap * sqrt(eta) * exp(0.5 * I * pi) * exp(2.0 * I * pi * (
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

        def get_model(time, x_pos, y_pos):
            """Return the data model for all wavelengths."""

            dit = self.dit
            wl_bin = self.wl_bin
            # eta_t = self.eta_t
            model = np.zeros((len(self.wavelengths), len(time)))
            for i, wavelength in enumerate(self.wavelengths):
                self.wavelength = wavelength
                model[i] = get_model_single(time, x_pos, y_pos) * wl_bin[i] * dit
            # if self.polyfits is not None:
            #     return model - a * self.polyfits[0]
            return model

        # Definitions
        #########################################################################
        # Working

        # Generate data
        phringe = PHRINGE()

        phringe.run(
            config_file_path=context.config_file_path,
            exoplanetary_system_file_path=context.exoplanetary_system_file_path,
            settings=context.simulation,
            observatory=context.instrument,
            observation=context.observation_mode,
            scene=context.scene,
            spectrum_files=context.spectrum_files,
            gpus=self.gpus,
            output_dir='',
            write_fits=False,
            create_copy=False,
            detailed=True
        )

        # Extract data from PHRINGE
        self._intensity_response = phringe.get_intensity_response()
        self.diff_ir = (self._intensity_response['Earth'][:, 2, :, :, :] - self._intensity_response['Earth'][:, 3, :, :,
                                                                           :]).numpy().astype(np.float64)
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

        # # Get analytical expression
        # expr = self.get_analytical_expr()
        # print(expr)
        # expr = self.get_analytical_expr_ir()
        # print(expr)

        # Initial guess
        # flux_real = (np.float64(phringe._director._planets[0].spectral_flux_density.cpu().numpy())).tolist()
        # flux_init = np.ones(len(self.wavelengths)) * 500000
        # flux_init = np.asarray(flux_real)
        times = phringe.get_time_steps().numpy()

        data = context.data[0].numpy().astype(np.float64)

        model = get_model(times, 3.4e-7, 3.4e-7)

        a = np.linalg.inv(model @ np.transpose(model))
        b = a @ model
        flux_est = b @ np.transpose(data)

        plt.imshow(flux_est)
        plt.colorbar()
        plt.show()

        return context
