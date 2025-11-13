import numpy as np
import torch
from matplotlib import pyplot as plt

from lifesimmc.core.modules.base_module import BaseModule
from lifesimmc.core.resources.base_resource import BaseResource
from lifesimmc.core.resources.data_resource import DataResource
from lifesimmc.core.resources.test_resource import TestResource


class NoiseSubtractionModule(BaseModule):
    """Class representation of the model subtraction module.

    Parameters
    ----------
    n_setup_in : str
        Name of the input configuration resource.
    n_data_in : str
        Name of the input data resource.
    n_planet_params_in : str
        Name of the input planet parameters resource.
    n_transformation_in : str or tuple[str]
        Name of the input transformation resource.
    n_test_out : str
        Name of the output test resource.
    pfa : float
        Probability of false alarm.
    """

    def __init__(
            self,
            n_setup_in: str,
            n_data_in: str,
            n_data_cov_in: str,
            n_planet_params_in: str,
            n_data_out: str,
    ):
        """Constructor method.

        Parameters
        ----------
        n_setup_in : str
            Name of the input configuration resource.
        n_data_in : str
            Name of the input data resource.
        n_planet_params_in : str
            Name of the input planet parameters resource.
        n_transformation_in : str or tuple[str]
            Name of the input transformation resource.
        """
        self.n_setup_in = n_setup_in
        self.n_data_in = n_data_in
        self.n_data_cov_in = n_data_cov_in
        self.n_planet_params_in = n_planet_params_in
        self.n_data_out = n_data_out

    def apply(self, resources: list[BaseResource]) -> DataResource:
        """Apply the energy detector test.

        Parameters
        ----------
        resources : list[BaseResource]
            List of resources.

        Returns
        -------
        TestResource
            The test resource.
        """
        print("Performing energy detector test...")

        # Extract all inputs
        r_config_in = self.get_resource_from_name(self.n_setup_in) if self.n_setup_in is not None else None
        r_planet_params_in = self.get_resource_from_name(
            self.n_planet_params_in) if self.n_planet_params_in is not None else None
        data_in = self.get_resource_from_name(self.n_data_in).get_data()
        data_cov_in = self.get_resource_from_name(self.n_data_cov_in).get_data()

        r_data_out = DataResource(self.n_data_out)

        cov = torch.cov(data_cov_in[0]).cpu().numpy()
        cal_meas = data_in[0, 0]

        mean = np.zeros(cov.shape[0])
        samples = np.random.multivariate_normal(mean, cov, size=data_in.shape[2])
        counts_boot = torch.tensor(samples, dtype=data_in.dtype, device=data_in.device).T

        counts_boot = counts_boot.cpu().numpy()

        counts_boot_norm = abs(counts_boot)

        avg = np.mean(counts_boot_norm, axis=1)

        avg /= np.max(avg)

        # counts_boot_norm = np.einsum('ij, j->ij', abs(counts_boot), np.sign(cal_meas))  # Normalize by calibration measurement

        counts_new = avg[:, None] * cal_meas[None, :].cpu().numpy()

        data_out = torch.tensor(data_in.cpu().numpy() - counts_new[None, :, :], dtype=data_in.dtype,
                                device=data_in.device)

        plt.imshow(data_out.cpu().numpy()[0], cmap='viridis', aspect='auto')
        plt.title('Noise Subtracted Data')
        plt.colorbar()
        plt.show()

        r_data_out.set_data(data_out)

        # cov_data = torch.cov(data_in[0]).cpu().numpy()
        # np.fill_diagonal(cov_data, 0)
        # # Compute mean covariance per variable:
        #
        # mean_covariances = cov_data.sum(axis=1) / (cov_data.shape[0] - 1)
        #
        # # plt.plot(mean_covariances)
        # # plt.title('Mean Covariances')
        # # plt.show()
        #
        # calibration_meas = data_in.cpu().numpy()[0, 0]
        #
        # # plt.plot(calibration_meas)
        # # plt.show()
        #
        # cal_data = np.einsum('i, j->ij', mean_covariances, calibration_meas)
        # cal_data /= np.max(cal_data)
        # cal_data *= np.max(data_in.cpu().numpy()[0])
        #
        # # plt.imshow(cal_data, cmap='viridis', aspect='auto')
        # # plt.colorbar()
        # # plt.show()
        #
        # data_out = torch.tensor(data_in.cpu().numpy() - cal_data[None, :, :], dtype=data_in.dtype,
        #                         device=data_in.device)
        #
        # r_data_out.set_data(data_out)
        # #
        # plt.imshow(data_in.cpu().numpy()[0], cmap='viridis', aspect='auto')
        # plt.title('0')
        # plt.colorbar()
        # plt.show()
        # #
        # plt.imshow(data_out.cpu().numpy()[0], cmap='viridis', aspect='auto')
        # plt.title('1')
        # plt.colorbar()
        # plt.show()

        print('Done')
        return r_data_out
