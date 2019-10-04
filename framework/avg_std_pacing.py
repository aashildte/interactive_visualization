"""

Åshild Telle / Simula Research Laboratory / 2019

"""

import glob
import itertools
import textwrap
import numpy as np
import matplotlib.pyplot as plt
import math

from .value_structure import valid_combination, get_all_combinations


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
        key_avg = key + ("Average", "Vector norm")
        key_std = key + ("Standard deviation", "Vector norm")
        key_pac = key + ("Pacing", "Vector norm")
        time = time_mapping[key]
        values_avg = param_mapping[key_avg]
        values_std = param_mapping[key_std]
        pacing = param_mapping[key_pac]
    except KeyError:
        print("No data found for key ", key)
        return

    labels = [k for k in key[:-1]]
    label_str = ", ".join(labels)
    label_str = '\n'.join(textwrap.wrap(label_str, 100))

    np.warnings.filterwarnings('ignore')

    minvalues = values_avg - values_std
    maxvalues = values_avg + values_std

    # special cases; TODO needs to be given as input
    
    minvalues = np.where(minvalues > 0, minvalues, np.zeros_like(minvalues))

    if "Xmotion" in key:
        maxvalues = np.where(maxvalues < 1, maxvalues, np.ones(maxvalues.shape))

    # special case end
    axis.plot(time, values_avg)
    if np.max(pacing) > 0:
        axis.plot(time, pacing)
    axis.fill_between(time, minvalues, \
            maxvalues, color='gray', alpha=0.5)
    axis.set_title(label_str)

    axis.set_ylabel(key[-1])


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

    _, plt_combinations = get_all_combinations(headers, checkboxes)

    num_plots = len(plt_combinations)
    _, axes = plt.subplots(num_plots, 1, figsize=(figsize[0], figsize[1]*num_plots), \
                               sharex=True, squeeze=False)
    axes = axes.flatten()

    for (axis, key) in zip(axes, plt_combinations):
        plot_values(key, axis, headers, True, \
                param_mapping, time_mapping)

    axes[-1].set_xlabel("Time ($ms$)")

    #for axis in axes:
    #    axis.legend(bbox_to_anchor=(0., 1.05, 1., .105), loc=3, \
    #              mode="expand", borderaxespad=0.)
    plt.tight_layout()
    plt.savefig("current_configuration.png", dpi=300)
    plt.show()
