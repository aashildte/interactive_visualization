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

    return key


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

    quantities, ms_points, dimensions = param_space[-3:]

    # iterate through all possible combinations
    # and save values accordingly
 
    for dataset in all_values:
	# across different input parameters
        assert list(dataset["input_params"].keys()) == input_params, \
                "Error: Input parameter spaces don't match up."

        key_ip = _populate_param_space(dataset["input_params"], param_space)

        # across different tracked output values
        assert list(dataset["output_values"].keys()) == quantities, \
                "Error: Output values spaces don't match up."

        key_qt = []

        for q in quantities:
            #key_qt.append(q)

            # because D, and maybe M, can vary:
            _, M, D = dataset["output_values"][q].shape

            for m in range(M):
                #key[-2] = ms_points[m]
                for d in range(D):
                    #key[-1] = dimensions[d]
                    key = key_ip + [q, ms_points[m], dimensions[d]]
                    param_mapping[tuple(key)] = \
                        dataset["output_values"][q][:, m, d]

        # + time
        time_mapping[tuple(key[:-3])] = dataset["time"]

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

    for n in range(len(param_list[-3])):
        plt_map[param_list[-3][n]] = n

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

    for h in headers:
        param_check[h] = False

    for k in checkboxes.keys():
        key1, _ = k.split(";")
        if checkboxes[k]:
            param_check[key1] = True

    for h in headers:
        if not param_check[h]:
            return False

    return True


def plot_values(key, axs, headers, plt_map, param_mapping, \
                time_mapping):
    """

    For each subplot, for each key ...

    Args:
        key - which combination to plot output for
        axs - list of axs for the different subplots; updated
            in this function
        headers - list of possible parameter groups
        plt_map - dictionary for which quantity that belongs
            to which subplot
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

    labels = [(l + ": " + k) for (l, k) in zip(\
                    (headers[:-3] + headers[-2:]),
                    (key[:-3] + key[-2:]))]

    label_str = ", ".join(labels)
    label_str = '\n'.join(textwrap.wrap(label_str, 100))

    i = plt_map[key[-3]]

    if i == 0:
        axs[i].plot(time, values, label=label_str)
    else:
        axs[i].plot(time, values)

    axs[i].set_ylabel(key[-3])

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
    N_plots = len(plt_map.keys())

    _, axs = plt.subplots(N_plots, 1, figsize=(figsize[0], \
                    figsize[1]*N_plots), sharex=True, squeeze=False)
    axs = axs.flatten()

    for key in plt_combinations:
        plot_values(key, axs, headers, plt_map, param_mapping, \
                    time_mapping)

    axs[-1].set_xlabel("Time ($ms$)")
    axs[0].legend(bbox_to_anchor=(0., 1.05, 1., .105), loc=3, \
                  mode="expand", borderaxespad=0.)
    plt.tight_layout()
    plt.savefig("current.png", dpi=300)
    plt.show()


def setup(widgets, files, figsize):
    """

    Setup for everything.

    Args:
        widgets - widgets module
        files - which files to give as input, list of npy files
        figsize - how to scale the output plots, tuple of x dimension
            overall and y dimension per plot.

    Returns:
        Function called to update plots
        Dictionary with strings as keys (given by
            headers + "; " + value); widget checkboxes as values
        Tabs for the checkboxes

    """

    all_values = read_values(files)
    headers, param_space, time_mapping, param_mapping = \
                define_param_mappings(all_values)

    checkboxes, tabs = setup_widgets(widgets, headers, param_space)

    update = lambda **kw: update_args(headers, param_mapping, \
                                      time_mapping, figsize, kw)

    return update, checkboxes, tabs
