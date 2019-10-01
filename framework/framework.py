"""

Åshild Telle / Simula Research Laboratory / 2019

"""

import glob
import itertools
import textwrap
import numpy as np
import matplotlib.pyplot as plt

from .value_structure import \
        read_values, define_param_mappings, setup_widgets


def setup(widgets, files, figsize, plt_setup):
    """

    Setup for everything.

    Args:
        widgets - widgets module
        files - which files to give as input, list of npy files
        figsize - how to scale the output plots, tuple of x dimension
            overall and y dimension per plot
        plt_setup - string:
            "ms_points" gives plotting setup as defined in ms_points
            "avg_std_pacing" gives plotting as defined in avg_std_pacing

    Returns:
        Function called to update plots
        Dictionary with strings as keys (given by
            headers + "; " + value); widget checkboxes as values
        Tabs for the checkboxes

    """

    
    plt_setup_options = ("ms_points", "avg_std_pacing")
    error_msg = "Error: plt_setup expected to be in" + \
            "{}.".format(plt_setup_options)
    assert plt_setup in plt_setup_options, error_msg
    
    if plt_setup == "ms_points":
        from .ms_points import update_args
        default_headers = ["Tracked quantity", "Measuring point", "Dimension"]
    else:
        from .avg_std_pacing import update_args
        default_headers = ["Metric"]

    all_values = read_values(files)
    param_headers, param_space, time_mapping, param_mapping = \
                define_param_mappings(all_values)

    print(time_mapping.keys())

    headers = param_headers + default_headers

    checkboxes, tabs = setup_widgets(widgets, headers, param_space)
    update = lambda **kw: update_args(headers, param_mapping, \
                                      time_mapping, figsize, kw)
    return update, checkboxes, tabs
