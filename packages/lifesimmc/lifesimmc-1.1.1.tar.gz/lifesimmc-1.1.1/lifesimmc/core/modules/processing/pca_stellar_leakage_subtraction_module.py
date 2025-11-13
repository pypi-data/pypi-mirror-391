import numpy as np
import torch
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from lifesimmc.core.modules.processing.base_transformation_module import BaseTransformationModule
from lifesimmc.core.resources.base_resource import BaseResource
from lifesimmc.core.resources.data_resource import DataResource
from lifesimmc.core.resources.template_resource import TemplateResource
from lifesimmc.core.resources.transformation_resource import TransformationResource


class PCAStellarLeakageSubtractionModule(BaseTransformationModule):
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
            n_data_in: str,
            n_data_out: str,
            principal_components: int = 2,
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
        self.n_data_in = n_data_in
        self.n_data_out = n_data_out
        self.principal_components = principal_components

    def apply(self, resources: list[BaseResource]) -> DataResource:
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

        data_in = self.get_resource_from_name(self.n_data_in).get_data()

        reconstructed_data = torch.zeros(data_in.shape, device=self.device, dtype=torch.float32)

        for i in range(len(data_in)):
            # Standardizing the data
            scaler = StandardScaler()
            data_std = scaler.fit_transform(data_in[i].cpu().numpy().T)

            # Performing PCA
            pca = PCA(n_components=data_std.shape[1])  # Use min to avoid exceeding dimensions
            principal_components = pca.fit_transform(data_std)

            # Zero out the first 10 components
            principal_components[:, :self.principal_components] = np.zeros(
                principal_components[:, :self.principal_components].shape)

            # Reconstruct the data from modified principal components
            data_pca = pca.inverse_transform(principal_components)

            # Reversing the standardization
            reconstructed_data[i] = torch.tensor(
                scaler.inverse_transform(data_pca),
                device=self.device,
                dtype=torch.float32
            ).T

            plt.imshow(reconstructed_data[0].cpu().numpy())
            plt.colorbar()
            plt.show()

        # Apply the whitening matrix to the data and templates
        r_data_out = DataResource(self.n_data_out)

        r_data_out.set_data(reconstructed_data)

        print('Done')
        return r_data_out
