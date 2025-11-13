import copy
from itertools import product

import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm

from lifesimmc.core.modules.base_module import BaseModule
from lifesimmc.core.context import Context


class PolynomialSubtractionModule2(BaseModule):
    """Class representation of the polynomial subtraction module."""

    def __init__(self):
        """Constructor method."""
        pass

    def apply(self, context) -> Context:
        """Apply the module.

        :param context: The context object of the pipeline
        :return: The (updated) context object
        """
        # Convert to numpy array
        context.data = context.data.numpy()

        # Calculate D_fit
        print('Subtracting polynomial fits...')
        context.templates_subtracted = copy.deepcopy(context.templates)

        for index_time in tqdm(range(len(context.data[0][0]))):
            for index_output in range(len(context.data)):
                data_spectral_column = np.nan_to_num(context.data[index_output][:, index_time])

                # Calculate polynomial fit
                coefficients = np.polyfit(
                    range(len(data_spectral_column)),
                    data_spectral_column,
                    3
                )
                fitted_function = np.poly1d(coefficients)

                # Subtract polynomial fit from data
                context.data[index_output][:, index_time] -= fitted_function(range(len(data_spectral_column)))

                # Loop through grid of templates
                for index_x, index_y in product(range(context.simulation.grid_size),
                                                range(context.simulation.grid_size)):
                    # Get template corresponding to grid position
                    template = \
                        [template for template in context.templates if template.x == index_x and template.y == index_y][
                            0]

                    # Get index of template in context.templates list
                    template_index = context.templates.index(template)

                    # Plot template before fit subtraction
                    if index_x == 8 and index_y == 4 and index_time == 0:
                        plt.plot(context.templates[template_index].data[index_output][:, index_time],
                                 context.instrument.wavelength_bin_centers, label='Template Pre-Subtraction')
                        plt.ylabel('Wavelength ($\mu$m)')
                        plt.xlabel('Photon Counts')
                        plt.title('Template Before Subtraction')
                        # plt.legend()
                        plt.show()

                    # Subtract polynomial fit from template
                    context.templates_subtracted[template_index].data[index_output][:,
                    index_time] -= fitted_function(range(len(data_spectral_column)))

        d_fit = np.reshape(context.data[0], (context.data.shape[1] * context.data.shape[2]))

        # Calculate A
        index_x = 8
        index_y = 31
        template = \
            [template for template in context.templates if template.x == index_x and template.y == index_y][
                0]

        a = np.zeros((context.data.shape[1] * context.data.shape[2], context.data.shape[1]))

        for wl in range(context.data.shape[1]):
            a[wl * context.data.shape[2]:wl * context.data.shape[2] + 100, wl] = template.data[0, wl, :]

        # Calculate a inverse
        a_inv = np.linalg.pinv(np.nan_to_num(a, nan=0.0))

        # Calculate S
        s = np.dot(a_inv, d_fit)

        plt.plot(s)
        plt.show()

        print('Done')
        return context
