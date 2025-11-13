import torch
from scipy.linalg import inv, sqrtm

from lifesimmc.core.modules.base_module import BaseModule
from lifesimmc.core.resources.base_resource import BaseResource
from lifesimmc.core.resources.covariance_resource import CovarianceResource
from lifesimmc.core.resources.data_resource import DataResource
from lifesimmc.core.resources.template_resource import TemplateResourceCollection, TemplateResource


class CovarianceCalculationModule(BaseModule):
    """Class representation of the base module.

    :param n_config_in: The name of the input configuration resource
    :param n_cov_out: The name of the output covariance resource
    """

    def __init__(
            self,
            n_config_in: str,
            n_data_in: str,
            n_template_in: str,
            n_cov_out: str,
            n_data_out: str,
            n_template_out: str,
            overwrite: bool = False
    ):
        """Constructor method.

        :param n_config_in: The name of the input configuration resource
        :param n_data_in: The name of the input data resource
        :param n_template_in: The name of the input template resource
        :param n_cov_out: The name of the output covariance resource
        :param n_data_out: The name of the output data resource
        :param n_template_out: The name of the output template resource
        :param overwrite: Whether to overwrite/delete the existing resources
        """
        self.n_config_in = n_config_in
        self.n_data_in = n_data_in
        self.n_template_in = n_template_in
        self.n_cov_out = n_cov_out
        self.n_data_out = n_data_out
        self.n_template_out = n_template_out
        self.overwrite = overwrite

    def apply(self, resources: list[BaseResource]) -> tuple:
        """Calculate the covariance of the data without the planet signal. This is done by generating a new data set
        without a planet. In reality, this could be achieved e.g. by observing a reference star.

        :param resources: The resources to apply the module to
        :return: The resource
        """
        print('Calculating covariance matrix...')

        r_config_in = self.get_resource_from_name(self.n_config_in)
        templates_in = self.get_resource_from_name(self.n_template_in).collection
        r_data_out = DataResource(self.n_data_out)
        rc_template_out = TemplateResourceCollection(
            self.n_template_out,
            'Collection of TemplateResources, one for each point in the grid'
        )

        # simulation = copy(config_in.simulation)
        # simulation.has_planet_signal = False
        #
        # phringe = PHRINGE()
        # phringe.run(
        #     config_file_path=config_in.config_file_path,
        #     simulation=simulation,
        #     instrument=config_in.instrument,
        #     observation_mode=config_in.observation_mode,
        #     scene=config_in.scene,
        #     gpu=self.gpu,
        #     write_fits=False,
        #     create_copy=False
        # )

        # Calculate covariance from first 5% of the data
        data_in = self.get_resource_from_name(self.n_data_in).get_data()
        fraction = int(0.2 * data_in.shape[2])
        data_in_red = data_in[:, :, :fraction]

        cov_out = CovarianceResource(self.n_cov_out)
        cov_out.cov = torch.zeros((data_in_red.shape[0], data_in_red.shape[1], data_in_red.shape[1]))
        cov_out.i_cov_sqrt = torch.zeros((data_in_red.shape[0], data_in_red.shape[1], data_in_red.shape[1]))

        for i in range(len(data_in_red)):
            cov_out.cov[i] = torch.cov(data_in_red[i])
            #
            # cov_out.i_cov_sqrt[i] = torch.tensor(
            #     cov_inv_sqrt(cov_out.cov[i].cpu().numpy()),
            #     device=config_in.phringe._director._device
            # )

            cov_out.i_cov_sqrt[i] = torch.tensor(
                inv(sqrtm(cov_out.cov[i].cpu().numpy())),
                device=r_config_in.phringe._director._device
            )

        # Remove these 5% from data and templates
        r_data_out.set_data(data_in[:, :, fraction:])
        for it, template in enumerate(templates_in):
            template_data = template.get_data()[:, :, fraction:]
            rc_template_out.collection.append(
                TemplateResource(
                    name='',
                    x_coord=template.x_coord,
                    y_coord=template.y_coord,
                    x_index=template.x_index,
                    y_index=template.y_index,
                    _data=template_data
                )
            )
            if self.overwrite:
                templates_in[it] = None

        print('Done')
        return cov_out, r_data_out, rc_template_out
