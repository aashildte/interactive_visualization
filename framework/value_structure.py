"""

Åshild Telle / Simula Research Laboratory / 2019

"""

import glob
import itertools
import textwrap
import numpy as np
import matplotlib.pyplot as plt


def read_values(files):
    """

    Reads npy files into a list of dictionaries. Ignores any files
    which is not a npy file (but does not check if the data in the
    relevant file is organized as expected).

    Args:
        files - relevant input files

    Returns:
        List of dictionaries

    """

    file_list = glob.glob(files)
    all_values = []

    for f_in in file_list:
        try:
            values = np.load(f_in, allow_pickle=True).item()
            all_values.append(values)
        except IOError:
            print("Error: Could not read file: ", f_in)
    return all_values


def define_param_space(values):
    """

    Defines a list in which we get or can fill inn the relevant
    parameter space information. For the input parameters, these are
    left open (empty sets); for the measuring points and dimensions,
    these are assumed to be general for all files and the information
    is added straight away.

    Args:
        values - *one* dictionary organized as outlined above

    Returns:
        List of headers for possible parameter choices
        A list of list, where each sublist is either an empty set or
            a list of possible parameters.

    """

    input_params = list(values["input_params"].keys())
    quantities = list(values["output_values"].keys())
    ms_points = values["ms_points"]
    dimensions = values["dimensions"]

    param_space = []

    for _ in input_params:
        param_space.append(set())

    param_space.append(quantities)
    param_space.append(ms_points)
    param_space.append(dimensions)

    return input_params, param_space


def _populate_param_space(input_params, param_space):
    """

    Args:
        input_params - dictionary giving information about
            the input parameter set for the data assessed
        param_space -

    Return
        key - part of key which is populated by this part
            of the parameter space

    """
    key = []
    for (i, elem) in enumerate(list(input_params.keys())):
        value = str(input_params[elem])
        key.append(value)
        param_space[i].add(value)

    return tuple(key)


def _populate_param_mapping(output_values, key_ip, param_space, param_mapping):
    """

    Args:
        output_values - quantities to plot, over different measuring points
           and different dimensions
        key_ip - input parameter key
        param_space - list of (list of) parameter choices
        param_mapping - dictionary to populate

    """
    quantities, ms_points, dimensions = param_space[-3:]
    for qtt in quantities:
        _, num_ms_pts, num_dims = output_values[qtt].shape

        for n_m in range(num_ms_pts):
            for n_d in range(num_dims):
                key = key_ip + (qtt, ms_points[n_m], dimensions[n_d])
                param_mapping[key] = \
                    output_values[qtt][:, n_m, n_d]



def define_param_mappings(all_values):
    """

    Defines the parameter space for tracked quantities, for corresponding
    time arrays as well as updating the parameter space according to
    input parameter values.

    Args:
         all_values - all dictionaries, all organized as outlined above

    Returns:
        List of headers for possible parameter choices
        List of parameter choices corresponding to these headers
        Dictionary for finding relevant time information (first
            N-3 elements of each key, where the key is a tuple with
            values from possible parameter choices)
        Dictionary for finding relevant value information (all N
            elements of each key, where the key is a tuple with
            values from possible parameter choices)

    """

    input_params, param_space = define_param_space(all_values[0])

    param_mapping = {}
    time_mapping = {}


    # iterate through all possible combinations
    # and save values accordingly

    for dataset in all_values:
	# across different input parameters
        assert list(dataset["input_params"].keys()) == input_params, \
                "Error: Input parameter spaces don't match up."

        key_ip = _populate_param_space(dataset["input_params"], param_space)

        # across different tracked output values
        assert list(dataset["output_values"].keys()) == param_space[-3], \
                "Error: Output values spaces don't match up."

        _populate_param_mapping(dataset["output_values"], key_ip, param_space, param_mapping)

        # + time
        time_mapping[key_ip] = dataset["time"]

    for (i, elem) in enumerate(param_space):
        param_space[i] = list(elem)

    headers = input_params + \
        ["Output value", "Measuring point", "Dimension"]

    return headers, param_space, time_mapping, param_mapping


def setup_widgets(widgets, headers, param_space):
    """

    Maps input parameter and parameter space to checkboxes.

    Args:
        widgets - widgets module
        headers - list of headers for possible parameter choices
        param_space - list of possible parameter values

    Returns:
        Dictionary of possible checkboxes; dictionary with
            strings as keys (given by headers + "; " + value)
        Tab widget for the checkboxes

    """

    tabs = widgets.Tab()
    children = []

    # input parameters

    checkboxes = {}

    for (i, elem) in enumerate(param_space):
        thisbox = []
        for value in param_space[i]:
            cbox = widgets.Checkbox(value=(value == elem[0]), \
                                    description=str(value), \
                                    disabled=False)
            checkboxes[headers[i] + ";" + str(value)] = cbox
            thisbox.append(cbox)

        children.append(widgets.VBox(thisbox))
        tabs.set_title(i, headers[i])

    tabs.children = children

    return checkboxes, tabs


def get_all_combinations(headers, checkboxes):
    """

    Generates keys for all combinations checked of in checkboxes.

    Args:
        headers - list of headers for possible parameter choices
        checkboxes - map generated via the widget interface

    Returns:
        Dictionary giving a mapping of which quantity of interest
            that belongs to which subplot
        List of all possible keys to be plotted

    """
    # we sort by input_params as keys

    inverse_map = {}
    for (i, elem) in enumerate(headers):
        inverse_map[elem] = i

    param_list = [[] for i in range(len(headers))]

    for k in checkboxes.keys():
        if checkboxes[k]:
            key1, key2 = k.split(";")
            param_list[inverse_map[key1]].append(key2)

    plt_map = {}

    for i in range(len(param_list[-3])):
        plt_map[param_list[-3][i]] = i

    return plt_map, list(itertools.product(*param_list))


def valid_combination(headers, checkboxes):
    """

    Logical requirement: For a value to be plotted, it needs
    a valid key, which is only the case if at least one box
    is checked under each tab.

    Args:
        headers - for recognization of relevant keys
        checkboxes - dictionary of which checkboxes that
            are checked

    Returns:
        Boolean value indicating if we have enough information

    """
    param_check = {}

    for header in headers:
        param_check[header] = False

    for key in checkboxes.keys():
        key1, _ = key.split(";")
        if checkboxes[key]:
            param_check[key1] = True

    for header in headers:
        if not param_check[header]:
            return False

    return True
