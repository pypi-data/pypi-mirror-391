import torch
from scipy.linalg import inv, sqrtm

from lifesimmc.core.modules.base_module import BaseModule
from lifesimmc.core.resources.base_resource import BaseResource
from lifesimmc.core.resources.covariance_resource import CovarianceResource


class CovarianceCalculationModule2(BaseModule):
    """Class representation of the base module.

    :param n_config_in: The name of the input configuration resource
    :param n_cov_out: The name of the output covariance resource
    """

    def __init__(
            self,
            n_config_in: str,
            n_cov_out: str,
            n_data_in: str,
            diagonal_only: bool = False,
            cut: int = 0
    ):
        """Constructor method.

        :param n_config_in: The name of the input configuration resource
        :param n_cov_out: The name of the output covariance resource
        :param diagonal_only: Whether to return the diagonal part of the covariance matrix only
        """
        self.n_config_in = n_config_in
        self.n_cov_out = n_cov_out
        self.n_data_in = n_data_in
        self.diagonal_only = diagonal_only
        self.cut = cut

    def apply(self, resources: list[BaseResource]) -> tuple:
        """Calculate the covariance of the data without the planet signal. This is done by generating a new data set
        without a planet. In reality, this could be achieved e.g. by observing a reference star.

        :param resources: The resources to apply the module to
        :return: The resource
        """
        print('Calculating covariance matrix...')

        config_in = self.get_resource_from_name(self.n_config_in)
        #
        # simulation = copy(config_in.simulation)
        # simulation.has_planet_signal = False
        #
        # # Generate random number and update torcha nd numpy seeds
        # if self.seed is None:
        #     seed = torch.randint(0, 2 ** 32, (1,)).item()
        # else:
        #     seed = (self.seed + 1) * 2
        #     if seed > 2 ** 32:
        #         seed = seed // 10
        #
        # torch.manual_seed(seed)
        # torch.cuda.manual_seed(seed)
        # torch.cuda.manual_seed_all(seed)
        # np.random.seed(seed)
        #
        # phringe = PHRINGE()
        # phringe.run(
        #     # config_file_path=config_in.config_file_path,
        #     simulation=simulation,
        #     instrument=config_in.instrument,
        #     observation_mode=config_in.observation_mode,
        #     scene=config_in.scene,
        #     seed=seed,
        #     # not the same as in data generation, but predictable
        #     gpu=self.gpu,
        #     write_fits=False,
        #     create_copy=False,
        #     extra_memory=20
        # )

        wavelengths = config_in.phringe.get_wavelength_bin_centers(as_numpy=True)

        # Calculate covariance from first 5% of the data
        data = self.get_resource_from_name(self.n_data_in).get_data()

        # data = phringe.get_data(as_numpy=False)
        cov_out = CovarianceResource(self.n_cov_out)
        cov_out.cov = torch.zeros((data.shape[0], data.shape[1], data.shape[1]))
        cov_out.i_cov_sqrt = torch.zeros((data.shape[0], data.shape[1], data.shape[1]))

        def func(x, a, b):
            return a + b * x ** (-5.2)

        for k in range(len(data)):
            cov = torch.cov(data[k])

            # diag = torch.diag(torch.diag(cov))
            #
            # cov = cov - diag
            #
            # cov[self.cut:-1, self.cut:-1] = 0
            #
            # cov = cov + diag

            # cov = torch.cov(data[k][:val])
            #
            # diag = torch.diag(cov)
            # wl_used = wavelengths[:val]
            #
            # print(wl_used)
            #
            # popt, pcov = curve_fit(func, wl_used, diag, p0=[1e5, 1e-11], maxfev=10000)
            #
            # print(popt)
            #
            # # make polyfit of diag
            # # coefficients = np.polyfit(
            # #     range(len(cov)),
            # #     diag,
            # #     4
            # # )
            # # fitted_function = np.poly1d(coefficients)
            #
            # plt.plot(wl_used, diag, label='diag')
            # plt.plot(wavelengths, func(wavelengths, *popt), label='fit')
            # # plt.plot(xx, func(xx, *popt), label='fit')
            # # plt.plot(range(data.shape[1]), fitted_function(range(data.shape[1])))
            # plt.legend()
            # plt.show()
            #
            # diag_extra = func(wavelengths, *popt)
            #
            # cov_extra = np.diag(diag_extra)
            #
            # # plt.imshow(cov_extra, cmap='plasma')
            # # plt.colorbar()
            # # plt.show()
            #
            # for i in range(len(wavelengths)):
            #     for j in range(len(wavelengths)):
            #         # if (i + j) % 2 == 0:
            #         cov_extra[i, j] = cov_extra[(i + j) // 2, (i + j) // 2]
            #
            # # plt.imshow(cov_extra, cmap='plasma')
            # # plt.colorbar()
            # # plt.show()
            #
            # for i in range(len(wavelengths)):
            #     for j in range(len(wavelengths)):
            #         if cov_extra[i, j] == 0:
            #             try:
            #                 # for upper boundary
            #                 if i - 1 < 0:
            #                     cov_extra[i, j] = (cov_extra[i, j - 1] + cov_extra[i + 1, j]) / 2
            #                 # for right boundary
            #                 elif j + 1 >= len(wavelengths):
            #                     cov_extra[i, j] = (cov_extra[i - 1, j] + cov_extra[i, j - 1]) / 2
            #                 else:
            #                     cov_extra[i, j] = (cov_extra[i - 1, j] + cov_extra[i, j + 1]) / 2
            #             except IndexError:
            #                 pass
            #
            # # Create a map of true and false, false wherever the value is 0
            # map = cov_extra == 0
            #
            # plt.imshow(map, cmap='plasma')
            # plt.colorbar()
            # plt.show()

            # stack the extra diag values wo create a square matrix
            # cov_extra = np.stack([diag_extra for _ in range(len(diag_extra))])
            #
            # # rotate values by 45 deg
            # cov_extra = rotate(cov_extra, angle=-45, reshape=False)
            #
            # a = (len(cov_extra) - len(wavelengths)) // 2
            #
            # print(a)
            #
            # cov_extra = cov_extra[a:data.shape[1] + a, a:data.shape[1] + a]
            # # cov_extra = cov_extra[:data.shape[1], :data.shape[1]]
            #
            # plt.imshow(cov_extra, cmap='plasma')
            # plt.colorbar()
            # plt.show()
            cov_extra = cov
            cov_extra = torch.tensor(cov_extra, device=config_in.phringe._director._device)

            cov_out.cov[k] = cov_extra

            if self.diagonal_only:
                cov_out.cov[k] = torch.diag(torch.diag(cov_out.cov[k]))

            cov_out.i_cov_sqrt[k] = torch.tensor(
                sqrtm(inv(cov_out.cov[k].cpu().numpy())),
                device=config_in.phringe._director._device
            )

        print('Done')
        return cov_out
