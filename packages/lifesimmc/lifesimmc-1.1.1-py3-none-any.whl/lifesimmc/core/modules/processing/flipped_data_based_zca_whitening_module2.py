from itertools import product

import numpy as np
import torch
from matplotlib import pyplot as plt
from scipy.linalg import sqrtm, inv
from tqdm import tqdm

from lifesimmc.core.modules.processing.base_transformation_module import BaseTransformationModule
from lifesimmc.core.resources.base_resource import BaseResource
from lifesimmc.core.resources.data_resource import DataResource
from lifesimmc.core.resources.template_resource import TemplateResource
from lifesimmc.core.resources.transformation_resource import TransformationResource


class FlippedDataBasedZCAWhiteningModule2(BaseTransformationModule):
    """Class representation of the ZCA whitening transformation module. This module applied ZCA whitening to the data
    and templates using a covariance matrix based on a calibration star. The properties of this calibration star are
    assumed to be identical to the properties of the target star.

    Parameters
    ----------

    n_setup_in : str
        Name of the input configuration resource.
    n_data_in : str
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
            n_data_in: str,
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
        n_data_in : str
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
        self.n_data_in = n_data_in
        self.n_template_in = n_template_in
        self.n_data_out = n_data_out
        self.n_template_out = n_template_out
        self.n_transformation_out = n_transformation_out
        self.diagonal_only = diagonal_only

    def apply(self, resources: list[BaseResource]) -> tuple[DataResource, TemplateResource, TransformationResource]:
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

        config_in = self.get_resource_from_name(self.n_config_in)

        data_in = self.get_resource_from_name(self.n_data_in).get_data()

        counts_orig = config_in.phringe.get_counts()
        a = counts_orig[2] - counts_orig[3]

        print(a[20, 21])
        print(data_in[0, 20, 21])

        data_sum = (counts_orig[2] + counts_orig[3])
        diff = data_in[0] - data_sum
        diff = counts_orig[2]
        diff = data_in[0]

        plt.imshow(diff.cpu().numpy(), aspect='auto')
        plt.colorbar()
        plt.show()

        plt.imshow(data_in[0].cpu().numpy(), aspect='auto')
        plt.colorbar()
        plt.show()

        diff_counts = torch.zeros(data_in.shape, device=self.device, dtype=torch.float32)
        # bounds = config_in.instrument.wavelength_bands_boundaries
        #
        # # Calculate the whitening matrix
        # cov_low = torch.zeros(
        #     (diff_counts.shape[0], diff_counts.shape[1], diff_counts.shape[1]),
        #     device=self.device,
        #     dtype=torch.float32
        # )
        i_cov_sqrt = torch.zeros(
            (diff_counts.shape[0], diff_counts.shape[1], diff_counts.shape[1]),
            device=self.device,
            dtype=torch.float32
        )

        # fit polynomial
        # rows, cols = diff_counts[0].shape  # should return (30, 100)
        #
        # x = np.arange(rows)  # shape (30,)
        #
        # degree = 2
        # fitted_data = np.zeros_like(data_in.cpu().numpy()[0])
        #
        # for col in range(cols):
        #     y = data_in[0].cpu().numpy()[:, col]  # shape (30,)
        #     coeffs = np.polyfit(x, y, degree)  # x and y both length 30
        #     fitted_data[:, col] = np.polyval(coeffs, x)
        #
        # plt.imshow(fitted_data)
        # plt.colorbar()
        # plt.show()
        #
        # # fitted_data = torch.tensor(fitted_data)
        # wl = config_in.instrument.wavelength_bin_centers.cpu().numpy()
        #
        # # extrapolate from lower
        # rows, cols = data_in.shape[1], data_in.shape[2]
        #
        # # Creating a synthetic pattern (polynomial + noise)
        # # x = np.arange(rows)
        # # data = np.zeros((rows, cols))
        # # for col in range(cols):
        # #     # Polynomial of degree 3 with noise
        # #     y = 5 - 0.5 * x + 0.01 * x ** 2 - 0.0001 * x ** 3 + np.random.normal(0, 0.5, rows)
        # #     data[:, col] = y
        #
        # cut = 10
        #
        # # Step 1: Zero out data after the first 4 rows
        # data = data_in[0].cpu().numpy()
        # data[cut:, :] = 0
        #
        # plt.imshow(data)
        # plt.colorbar()
        # plt.show()
        #
        # def model_func(x, a):
        #     return a * (x.astype(float)) ** (-4)
        #
        # # Step 2: Fit a polynomial to the first 4 rows of each column and extrapolate
        # fitted_data = np.zeros_like(data)
        #
        # for col in range(cols):
        #     # Extract the first 4 non-zero values
        #     y_initial = data[:cut, col]
        #     x_initial = wl[:cut]
        #
        #     # Fit a polynomial of degree 3 to these points
        #     # coeffs = np.polyfit(x_initial, y_initial, 3)
        #
        #     popt, pcov = curve_fit(model_func, x_initial, y_initial)
        #
        #     # Extract the fitted parameter 'a'
        #     a_fit = popt[0]
        #     print(f"Fitted parameter a: {a_fit}")
        #
        #     # Generate fitted values
        #     fitted_y = model_func(wl, a_fit)
        #
        #     # Extrapolate to the full range
        #     # fitted_data[:, col] = np.polyval(coeffs, x)
        #     fitted_data[:, col] = fitted_y
        #
        # fitted_data = torch.tensor(fitted_data, device=self.device, dtype=torch.float32)
        #
        # plt.imshow(fitted_data.cpu().numpy())
        # plt.colorbar()
        # plt.show()
        #
        # diff_counts[0] = fitted_data

        ########
        #
        # counts = copy(data_in[0])
        #
        # cov_true = torch.cov(counts).cpu().numpy()
        #
        # L, T = counts.shape
        #
        # eigvals = np.linalg.eigvalsh(cov_true)
        #
        # if np.any(eigvals <= 0):
        #     cov_true += 1e-6 * np.eye(L)  # Regularization
        # num_samples = T  # Same number of time points
        # mean_vector = np.zeros(L)  # Assume zero mean
        # countsb = np.random.multivariate_normal(mean_vector, cov_true, size=num_samples).T  # Shape (L, T)
        # countsb = torch.tensor(countsb, device=self.device, dtype=torch.float32)
        ########

        # # PCA subtraction
        # pc = 1
        #
        # # Standardizing the data
        # scaler = StandardScaler()
        # data_std = scaler.fit_transform(data_in[0].cpu().numpy().T)
        #
        # # Performing PCA
        # pca = PCA(n_components=data_std.shape[1])  # Use min to avoid exceeding dimensions
        # principal_components = pca.fit_transform(data_std)
        #
        # # Zero out the first 10 components
        # principal_components[:, pc:] = np.zeros(principal_components[:, pc:].shape)
        #
        # # Reconstruct the data from modified principal components
        # data_low_rank = pca.inverse_transform(principal_components)
        #
        # # Reversing the standardization
        # data_low_rank = torch.tensor(
        #     scaler.inverse_transform(data_low_rank),
        #     device=self.device,
        #     dtype=torch.float32
        # ).T
        #
        # plt.imshow(data_in[0].cpu().numpy() - data_low_rank.cpu().numpy())
        # plt.colorbar()
        # plt.show()

        r_data_out = DataResource(self.n_data_out)
        for i in range(len(diff_counts)):
            data_sub = data_in[0]
            # fit data and get cov from this

            # for j in range(2):
            #
            #     if j == 0:
            #
            #         data_sub = copy(data_in[i, :13, :])
            #     else:
            #         data_sub = copy(data_in[i, 13:, :])
            #
            #     cov_low = torch.cov(data_sub)
            #
            #     if self.diagonal_only:
            #         cov_low = torch.diag(torch.diag(cov_low))

            # # set the first 10 elements in both dimensions to zero from cov
            # x_max = 2  # das kannst du ändern
            #
            # # Maske: alle Punkte mit i + j <= x_max
            # ny, nx = cov[i].shape
            # y, x = np.meshgrid(np.arange(ny), np.arange(nx), indexing="ij")
            # mask = (x + y) <= x_max
            #
            # for j in range(len(cov[i])):
            #     mask[j][j] = 1
            # # Set everything else to 0
            # # cov[i][~mask] = 0

            # plt.imshow(mask)
            # plt.colorbar()
            # plt.show()

            # plt.imshow(cov_low.cpu().numpy())
            # plt.colorbar()
            # plt.show()
            #
            # plt.imshow(cov_true)
            # plt.colorbar()
            # plt.show()
            #
            # plt.imshow(pinv(cov_low.cpu().numpy()))
            # plt.colorbar()
            # plt.show()

            # Setze den Bereich im Dreieck auf 0
            # cov[i][mask] = 0

            cov_low = torch.cov(diff) / 2

            i_cov_sqrt[0] = torch.tensor(sqrtm(inv(cov_low.cpu().numpy())), device=self.device,
                                         dtype=torch.float32)

            # plt.imshow(i_cov_sqrt[0].cpu().numpy())
            # plt.colorbar()
            # plt.show()

            # Apply the whitening matrix to the data and templates

            # for i in range(data_in.shape[0]):
            # plt.imshow(data_sub.cpu().numpy(), aspect='auto')
            # plt.colorbar()
            # plt.show()
            diff_counts[0] = i_cov_sqrt @ data_sub

            # plt.imshow(data_sub.cpu().numpy(), aspect='auto')
            # plt.colorbar()
            # plt.show()

            r_data_out.set_data(diff_counts)

        if self.n_template_in and self.n_template_out:
            r_template_in = self.get_resource_from_name(self.n_template_in)
            template_data_in = r_template_in.get_data()
            template_counts_white = torch.zeros(template_data_in.shape, device=self.device, dtype=torch.float32)

            for i, j in tqdm(
                    product(range(template_data_in.shape[-2]), range(template_data_in.shape[-1])),
                    total=template_data_in.shape[-2] * template_data_in.shape[-1]
            ):
                for k in range(template_data_in.shape[0]):
                    template_counts_white[k, :, :, i, j] = i_cov_sqrt[k] @ template_data_in[k, :, :, i, j]

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
                i2 = i_cov_sqrt.cpu().numpy()
            else:
                i2 = i_cov_sqrt
            for l in range(data.shape[0]):
                data[l] = i2[l] @ data[l]
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
