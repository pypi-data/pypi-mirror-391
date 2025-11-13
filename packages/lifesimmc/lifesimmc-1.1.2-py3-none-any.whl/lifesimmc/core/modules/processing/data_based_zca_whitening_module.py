from itertools import product
from typing import Union

import numpy as np
import torch
from scipy.linalg import sqrtm, inv
from tqdm import tqdm

from lifesimmc.core.modules.processing.base_transformation_module import BaseTransformationModule
from lifesimmc.core.resources.base_resource import BaseResource
from lifesimmc.core.resources.data_resource import DataResource
from lifesimmc.core.resources.template_resource import TemplateResource
from lifesimmc.core.resources.transformation_resource import TransformationResource


class DataBasedZCAWhiteningModule(BaseTransformationModule):
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

        data_cov_in = self.get_resource_from_name(self.n_data_cov_in).get_data()
        data_whiten_in = self.get_resource_from_name(self.n_data_whiten_in).get_data()

        i_cov_sqrt = torch.zeros(
            (data_cov_in.shape[0], data_cov_in.shape[1], data_cov_in.shape[1]),
            device=self.device,
            dtype=torch.float32
        )

        r_data_out = DataResource(self.n_data_out)

        # Whiten data
        for i in range(len(data_cov_in)):

            cov_low = torch.cov(data_cov_in[i])

            if self.diagonal_only:
                cov_low = torch.diag(torch.diag(cov_low))

            i_cov_sqrt[i] = torch.tensor(
                sqrtm(inv(cov_low.cpu().numpy())),
                device=self.device,
                dtype=torch.float32
            )

            data_whiten_in[i] = i_cov_sqrt[i] @ data_whiten_in[i]

        r_data_out.set_data(data_whiten_in)

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
