from copy import copy
from itertools import product
from typing import Union

import numpy as np
import torch
from sklearn.decomposition import PCA
from tqdm import tqdm

from lifesimmc.core.modules.processing.base_transformation_module import BaseTransformationModule
from lifesimmc.core.resources.base_resource import BaseResource
from lifesimmc.core.resources.data_resource import DataResource
from lifesimmc.core.resources.template_resource import TemplateResource
from lifesimmc.core.resources.transformation_resource import TransformationResource


class PCASubtractionModule(BaseTransformationModule):
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
            # n_data_cov_in: str,
            n_data_in: str,
            n_data_out: str,
            n_transformation_out: str = None,
            n_template_in: str = None,
            n_template_out: str = None,
            # diagonal_only: bool = False
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
        # self.n_data_cov_in = n_data_cov_in
        self.n_data_in = n_data_in
        self.n_template_in = n_template_in
        self.n_data_out = n_data_out
        self.n_template_out = n_template_out
        self.n_transformation_out = n_transformation_out
        # self.diagonal_only = diagonal_only

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

        data_in = self.get_resource_from_name(self.n_data_in).get_data().cpu().numpy()
        data = copy(data_in[0])

        n_subtract = 10
        n_components = data.shape[0]
        components_to_subtract = list(np.linspace(0, n_subtract - 1, n_subtract).astype(int))
        data -= np.mean(data, axis=0)
        pca = PCA(n_components=n_components)

        def pca_transform(data):
            data = data.copy()
            data -= np.mean(data, axis=0)  # Center the data
            modified_data = pca.fit_transform(data).copy()
            for comp in components_to_subtract:
                modified_data[:, comp] = 0
            return torch.tensor(pca.inverse_transform(modified_data)[None, :, :], device=self.device,
                                dtype=torch.float32)

        def pca_transform_template(template):
            template = template.copy()
            # template -= np.mean(template)  # Center template itself first (global mean)
            # template = template / np.std(template) * np.std(data_in[0])  # Scale energy to match data
            template -= np.mean(data_in[0], axis=0)
            # template -= np.mean(template, axis=0)  # Center the template
            modified_template = pca.transform(template)
            for comp in components_to_subtract:
                modified_template[:, comp] = 0
            return torch.tensor(pca.inverse_transform(modified_template), device=self.device,
                                dtype=torch.float32)

        # transformed_data = pca.fit_transform(data)
        # modified_data = transformed_data.copy()
        # for comp in components_to_subtract:
        #     modified_data[:, comp] = 0
        #
        # # Reconstruct the data
        # reconstructed_data = pca.inverse_transform(modified_data)

        r_data_out = DataResource(self.n_data_out)

        data_out = pca_transform(data_in[0])

        r_data_out.set_data(data_out)

        # Whiten templates if given
        if self.n_template_in and self.n_template_out:

            r_template_in = self.get_resource_from_name(self.n_template_in)
            template_data_in = r_template_in.get_data()
            template_counts_white = torch.zeros(template_data_in.shape, device=self.device, dtype=torch.float32)

            for i, j in tqdm(
                    product(range(template_data_in.shape[-2]), range(template_data_in.shape[-1])),
                    total=template_data_in.shape[-2] * template_data_in.shape[-1]
            ):
                for k in range(template_data_in.shape[0]):
                    # scaling_factor = np.std(data_out[0].cpu().numpy()) / np.std(
                    #     template_data_in[k, :, :, i, j].cpu().numpy())
                    #
                    template_counts_white[k, :, :, i, j] = pca_transform_template(
                        template_data_in[k, :, :, i, j].cpu().numpy())
                    # template_counts_white[k, :, :, i, j] = template_data_in[k, :, :, i, j]

                    # plt.imshow(template_counts_white[k, :, :, i, j].cpu().numpy(), cmap='viridis', aspect='auto')
                    # plt.colorbar()
                    # plt.title(f'Template {k}, Pixel ({i}, {j})')
                    # plt.show()

            r_template_out = TemplateResource(
                name=self.n_template_out,
                grid_coordinates=r_template_in.grid_coordinates
            )
            r_template_out.set_data(template_counts_white)
        else:
            r_template_out = None

        # Save the whitening transformation
        def pca_whitening_transformation(data2):
            """Apply the ZCA whitening transformation."""
            if isinstance(data2, np.ndarray):
                pass
            else:
                data2 = data2.cpu().numpy()
            for l in range(data2.shape[0]):
                data2[l] = pca_transform_template(data2[l]).cpu().numpy()
            return data2

        pca2 = pca_whitening_transformation

        r_transformation_out = TransformationResource(
            name=self.n_transformation_out,
            transformation=pca2
        )

        print('Done')
        if r_template_out is not None:
            return r_data_out, r_template_out, r_transformation_out
        return r_data_out, r_transformation_out
