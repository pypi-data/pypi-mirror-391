import emcee
import numpy as np
import torch

from lifesimmc.core.modules.base_module import BaseModule
from lifesimmc.core.resources.base_resource import BaseResource
from lifesimmc.core.resources.planet_params_resource import PlanetParamsResource, PlanetParams


class MCMCModule(BaseModule):
    def __init__(self, n_setup_in: str, n_data_in: str, n_planet_params_out: str,
                 n_transformation_in: str = None, n_template_in: str = None,
                 n_planet_params_in: str = None):
        super().__init__()
        self.n_config_in = n_setup_in
        self.n_data_in = n_data_in
        self.n_template_in = n_template_in
        self.n_transformation_in = n_transformation_in
        self.n_planet_params_out = n_planet_params_out
        self.n_planet_params_in = n_planet_params_in

    def apply(self, resources: list[BaseResource]) -> PlanetParamsResource:
        print('Running MCMC parameter estimation...')

        r_config_in = self.get_resource_from_name(self.n_config_in)
        r_templates_in = self.get_resource_from_name(self.n_template_in)
        r_transformation_in = self.get_resource_from_name(
            self.n_transformation_in) if self.n_transformation_in else None
        transf = r_transformation_in.transformation if r_transformation_in else lambda x: x
        planet_params_in = self.get_resource_from_name(self.n_planet_params_in) if self.n_planet_params_in else None

        times = r_config_in.phringe.get_time_steps().cpu().numpy()
        wavelengths = r_config_in.phringe.get_wavelength_bin_centers().cpu().numpy()
        wavelength_bin_widths = r_config_in.phringe.get_wavelength_bin_widths().cpu().numpy()
        data_in = self.get_resource_from_name(self.n_data_in).get_data()
        template_data = r_templates_in.get_data()

        data_in = data_in.permute(0, 2, 1).reshape((-1,) + data_in.shape[2:]).cpu().numpy()

        if planet_params_in is None:
            raise NotImplementedError("Please provide initial planet parameters.")
        else:
            flux_init = planet_params_in.params[0].sed.cpu().numpy()
            semi_major_axis_init = planet_params_in.params[0].semi_major_axis
            inclination_init = planet_params_in.params[0].inclination
            eccentricity_init = planet_params_in.params[0].eccentricity
            raan_init = planet_params_in.params[0].raan
            argument_of_periapsis_init = planet_params_in.params[0].argument_of_periapsis
            true_anomaly_init = planet_params_in.params[0].true_anomaly
            planet_mass_init = planet_params_in.params[0].mass

        def log_prior(theta):
            flux = theta[:len(flux_init)]
            sma, incl, ecc, raan, argp, ta, mass = theta[len(flux_init):]

            if not (1e9 < sma < 1e12 and 0 <= incl <= np.pi and 0 <= ecc < 1 and
                    0 <= raan <= 2 * np.pi and 0 <= argp <= 2 * np.pi and
                    0 <= ta <= 2 * np.pi and 1e23 <= mass < 1e25):
                return -np.inf
            if np.any(flux < 0):
                return -np.inf
            return 0.0  # flat prior

        def log_likelihood(theta):
            flux = theta[:len(flux_init)]
            sma, incl, ecc, raan, argp, ta, mass = theta[len(flux_init):]
            try:
                model = r_config_in.phringe._get_template_diff_counts(
                    times=times,
                    wavelength_bin_centers=wavelengths,
                    wavelength_bin_widths=wavelength_bin_widths,
                    flux=flux,
                    has_orbital_motion=True,
                    semi_major_axis=sma,
                    inclination=incl,
                    eccentricity=ecc,
                    raan=raan,
                    argument_of_periapsis=argp,
                    true_anomaly=ta,
                    host_star_distance=r_config_in.phringe._scene.star.distance,
                    host_star_mass=r_config_in.phringe._scene.star.mass,
                    planet_mass=mass,
                )
            except RuntimeError:
                return -np.inf

            model = transf(model)
            model = np.transpose(model, (0, 2, 1)).reshape(data_in.shape)
            residual = model - data_in
            return -0.5 * np.sum(residual ** 2)

        def log_probability(theta):
            lp = log_prior(theta)
            return lp + log_likelihood(theta) if np.isfinite(lp) else -np.inf

        ndim = len(flux_init) + 7
        nwalkers = 2 * ndim
        initial = np.concatenate([flux_init, [
            semi_major_axis_init,
            inclination_init,
            eccentricity_init,
            raan_init,
            argument_of_periapsis_init,
            true_anomaly_init,
            planet_mass_init
        ]])
        p0 = initial + 1e-4 * np.random.randn(nwalkers, ndim)

        sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability)
        sampler.run_mcmc(p0, 500, progress=True)
        samples = sampler.get_chain(discard=100, flat=True)

        # Compute median and 1-sigma intervals
        medians = np.median(samples, axis=0)
        q16, q84 = np.percentile(samples, [16, 84], axis=0)
        err_low = medians - q16
        err_high = q84 - medians

        # Output values
        fluxes = medians[:len(flux_init)]
        flux_err = 0.5 * (err_low[:len(flux_init)] + err_high[:len(flux_init)])
        orbit_params = medians[len(flux_init):]
        orbit_errs = 0.5 * (err_low[len(flux_init):] + err_high[len(flux_init):])

        # Logging
        names = ["sma", "incl", "ecc", "raan", "argp", "ta", "mass"]
        for name, val, err in zip(names, orbit_params, orbit_errs):
            print(f"{name}: {val:.4f} ± {err:.4f}")

        # Construct output resource
        r_planet_params_out = PlanetParamsResource(name=self.n_planet_params_out)
        planet_params = PlanetParams(
            name='',
            sed_wavelength_bin_centers=r_config_in.phringe.get_wavelength_bin_centers(),
            sed_wavelength_bin_widths=r_config_in.phringe.get_wavelength_bin_widths(),
            sed=torch.tensor(fluxes),
            sed_err_low=torch.tensor(flux_err),
            sed_err_high=torch.tensor(flux_err),
            semi_major_axis=orbit_params[0],
            inclination=orbit_params[1],
            eccentricity=orbit_params[2],
            raan=orbit_params[3],
            argument_of_periapsis=orbit_params[4],
            true_anomaly=orbit_params[5],
            mass=orbit_params[6],
        )
        r_planet_params_out.params.append(planet_params)

        return r_planet_params_out
