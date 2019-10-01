"""

Åshild Telle / Simula Research Laboratory / 2019

"""

import glob
import itertools
import textwrap
import numpy as np
import matplotlib.pyplot as plt

from .value_structure import valid_combination


def plot_values(key, axis, headers, set_label, param_mapping, \
                time_mapping):
    """

    For each subplot, for each key ...

    Args:
        key - which combination to plot output for
        axis - list of axes for the different subplots; updated
            in this function
        headers - list of possible parameter groups
        set_label; boolean value - set label or not
        param_mapping - dictionary with keys as values,
            quantities as values; subtract information to
            be plotted from this
        time mapping - same, with the corresponding time array

    """


    try:
        time = time_mapping[key[:-3]]
        values = param_mapping[key]
    except KeyError:
        print("No data found for key ", key)
        return

    if set_label:
        labels = [(l + ": " + k) for (l, k) in zip(\
                    (headers[:-3] + headers[-2:]),
                    (key[:-3] + key[-2:]))]

        label_str = ", ".join(labels)
        label_str = '\n'.join(textwrap.wrap(label_str, 100))

        axis.plot(time, values, label=label_str)
    else:
        axis.plot(time, values)

    axis.set_ylabel(key[-3])


def update_args(headers, param_mapping, time_mapping, figsize, \
                checkboxes):
    """

    Update function with a few extra parameters that needs to be
    set in advance + checkboxes which is set for every update.

    Args:
        headers - list of headers for possible parameter choices
        param_mapping - dictionary with keys from given parameter
            space as values, quantities as values
        time_mapping - dictionary with keys from given parameter
            space as values, time arrays as values
        figsize - specify to control size of output plots
        checkboxes - dictionary with strings as keys (given by
            headers + "; " + value); widget checkboxes as values

    """
    plt.clf()

    if not valid_combination(headers, checkboxes):
        print("Please check at least one box in each group")
        return

    plt_map, plt_combinations = get_all_combinations(headers, checkboxes)
    num_plots = len(plt_map.keys())

    _, axes = plt.subplots(num_plots, 1, figsize=(figsize[0], \
                    figsize[1]*num_plots), sharex=True, squeeze=False)
    axes = axes.flatten()

    for key in plt_combinations:
        axis = axes[plt_map[key[-3]]]
        plot_values(key, axis, headers, plt_map[key[-3]] == 0, \
                param_mapping, time_mapping)

    axes[-1].set_xlabel("Time ($ms$)")
    axes[0].legend(bbox_to_anchor=(0., 1.05, 1., .105), loc=3, \
                  mode="expand", borderaxespad=0.)
    plt.tight_layout()
    plt.savefig("current.png", dpi=300)
    plt.show()


