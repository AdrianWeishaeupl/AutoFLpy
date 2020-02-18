import pandas as pd
import textwrap
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as interp
from requests import  HTTPError
from mpl_toolkits.axes_grid1 import make_axes_locatable
import autoflpy.util.analysis.take_off_detection as take_off_detection

try:
    import geopandas as gpd
    import contextily as ctx
    from pyproj import Proj as proj, transform
    map_modules_imported = True
except ImportError:
    map_modules_imported = False


def graph_plotter(plot_information, values_list, x_limits=("x_min", "x_max"),
                  y_limits=("y_min", "y_max"), marker_list=(), scale=0.01,
                  map_info=("altitude", "gps"), map_info_limits=(None, None), arm_data=False,
                  title_text=None):
    """ Goes through graph data, finds source and gets required data from
    values. plot information structure, [x, name, data_source].

    scale represents the amount of zoom on the second latitude longitude plot
    if this is present.

    map_info represents additional information requested by the user to be plotted as a colour bar on the map line.
    The default is gps altitude data. Structure = [name, data_source].

    map_info_limits are limits to be applied in to the map_info data in the form [lower_limit, upper_limit]. If only
    one limit is required, enter the other limit as None. This colours any points below the lower_limit in blue and any
    above the upper_limit in red.

    arm_data is an additional function to display when the UAV was armed/disarmed. This works if the EV (Event) data
    is has been recorded and is present in the Data_sources.txt document.

    title_text allows the user to give figures custom titles in the form of a string.
    """
    # TODO: KEEP AN EYE ON THESE:
    title = None
    x = None
    y = None
    reference_y_unit = None
    reference_x_unit = None
    reference_x_heading = None
    arm_plot_data = None
    plot_data_map = None
    xlabel = None

    # List of data to plot returns plot data which has structure:
    # [axis, [data_source, column]]
    plot_data = []
    plt.rcParams["figure.figsize"] = (15, 3)

    if arm_data is True:

        # Imports data for the arming/disarming if it is present.
        arm_info = [["id", "ev"], ["time", "ev"]]
        arm_plot_data = []
        index = []
        for index in arm_info:
            values_list_index = 0
            # sets value_found to a default of False
            # Checks to see if the 'data source' recorded in the graph list
            # matches the 'data sources' in the list structure values_list.
            for values_list_data in values_list:
                # Finds data source.
                if index[1] == values_list_data[0].lower():
                    index.append(values_list_index)
                    # Finds corresponding time source.
                    # Goes through each column searching for a match.
                    for column in values_list[values_list_index][1:]:
                        # Checks to see if they have the same title.
                        if column[0].lower() == index[0]:
                            # if they do then the data is appended.
                            arm_plot_data.append(column)
                            # exits for loop if data has been appended.
                            break
                values_list_index += 1
    if arm_data is True:
        if len(arm_plot_data) != 0:
            arm_data = True
        else:
            # Data has not been imported properly or is not present.
            print("Arm data is not present or has not been imported properly. Make sure \"EV\" is present in the "
                  "Data_sources.txt file, then run autoflpy again to re-generate the data.")
            # Sets arm_data to false.
            arm_data = False

    for data in plot_information:
        values_list_index = 0
        # sets value_found to a default of False
        # Checks to see if the 'data source' recorded in the graph list
        # matches the 'data sources' in the list structure values_list.
        for values_list_data in values_list:
            # Finds data source.
            if data[2] == values_list_data[0].lower():
                data.append(values_list_index)
                # Goes through each column searching for a match.
                for column in values_list[values_list_index][1:]:
                    # Checks to see if they have the same title.
                    if column[0].lower() == data[1]:
                        # if they do then the data is appended.
                        plot_data.append([data[0], column, data[2]])
                        # exits for loop if data has been appended.
                        break
            values_list_index += 1

    # Checks if the plot in question is a map plot
    if len(plot_data) != 0:
        if "Latitude" in [plot_data[0][1][0], plot_data[1][1][0]]:
            if "Longitude" in [plot_data[0][1][0], plot_data[1][1][0]]:
                mapplot_active = True
            else:
                mapplot_active = False
        else:
            mapplot_active = False
    else:
        mapplot_active = False

    # Imports the map data used for colouring the line on the latitude-longitude plot.
    if len(map_info) == 2 and mapplot_active is True:
        # Adds data series to be called for the time of the map_info and GPS time (later used for interpolating
        # the data)
        map_info = [map_info, ["time", str(map_info[1])], ["time", "gps"]]
        try:
            data_map = []
            plot_data_map = []
            for index in map_info:
                values_list_index = 0
                # sets value_found to a default of False
                # Checks to see if the 'data source' recorded in the graph list
                # matches the 'data sources' in the list structure values_list.
                for values_list_data in values_list:
                    # Finds data source.
                    if index[1] == values_list_data[0].lower():
                        data_map.append(values_list_index)
                        # Finds corresponding time source.
                        # Goes through each column searching for a match.
                        for column in values_list[values_list_index][1:]:
                            # Checks to see if they have the same title.
                            if column[0].lower() == index[0]:
                                # if they do then the data is appended.
                                plot_data_map.append(column)
                                # exits for loop if data has been appended.
                                break
                    values_list_index += 1
        except IndexError:
            print('map_info input variables not found. Check the input spelling and that the variable exists.')
    elif map_info != 2 and mapplot_active is True:
        print('map_info variable entered incorrectly. Format should be: map_info=["data", "data_set"].')
    else:
        pass

    # Goes through the graph list and finds the matching values in the values_
    # list and then appends these values to a new list with x or y stated.
    # returns plot data which has structure: [axis, [data_source, column]]
    # This will go through all the data and plot it.
    # Plot info is used to inform the code what graph style that it
    # needs to plot. A final plot info of 0 means that the combination of
    # x and y values is invalid and so the cell will be automatically
    # removed. A final plot info of 1 means that there is just x and y,
    # a final plot info of 2 means that there are n x values which must
    # have the same name and unit (ie be the same information as the first
    # x but from a different data source) and multiple y values with the
    # same unit. A final plot info of 3 means that there are multiple y
    # values which do not have the same unit and n x values which must have
    # the same name and unit.
    plot_info = 0
    # checks the length of the cell, if there is one x and y value to
    # plot
    if len(plot_data) == 2:
        plot_info = 1
    if len(plot_data) > 2:
        plot_info = 2
    # Used to count the number of Xs
    x_count = 0
    for xy in plot_data:
        if xy[0] == "x":
            x_count += 1
    # if x count equals to 0 then plot info is set to 0
    if x_count == 0:
        plot_info = 0
    # If there is more than 1 x value
    if x_count > 1:
        first_x_unit = True
        if plot_info == 2:
            # Check through the cells that contain x.
            for xy_data in plot_data:
                if xy_data[0] == "x":
                    # Check if this is the first x value unit that has been
                    # evaluated.
                    if first_x_unit is True:
                        # If it is then it sets it to be the reference unit
                        reference_x_unit = xy_data[1][1]
                        # Sets a reference heading for the x data.
                        reference_x_heading = xy_data[1][0]
                        first_x_unit = False
                    else:
                        # Sets the unit of the next item
                        unit = xy_data[1][1]
                        # Sets the heading of the next item
                        heading = xy_data[1][0]
                        if reference_x_unit == unit and reference_x_heading == heading:
                            plot_info = 2
                        else:
                            # Removes graph if the x values provided have
                            # different units.
                            plot_info = 0
                            break
        else:
            # If there are two variables (plot info = 1) and both variables are
            # x variables then do not plot the data.
            plot_info = 0
    # Sets first unit to True, so that the reference values are recorded when
    # the first lot of y data arrives.
    first_y_unit = True
    # If there is more than 1 y value
    if plot_info == 2:
        # Check through the cells that contain y.
        for xy_data in plot_data:
            if xy_data[0] == "y":
                # Check if this is the first unit
                if first_y_unit is True:
                    # If it is then it sets it to be the reference unit.
                    reference_y_unit = xy_data[1][1]
                    first_y_unit = False
                else:
                    # If this is the second y value found.
                    unit = xy_data[1][1]
                    # If the units are constant then plot them together
                    if reference_y_unit == unit:
                        plot_info = 2
                    else:
                        plot_info = 3
                        break
    # Counts number of x.
    x_list = []
    # Counts number of y.
    y_list = []
    for xy_data in plot_data:
        # Checks to see what plot info equals.
        if plot_info == 1:
            # Checks to see if the current data being viewed is y data
            if xy_data[0] == "x":
                x = xy_data[1]
            # Checks to see if the data being viewed is x data.
            if xy_data[0] == "y":
                y = xy_data[1]
        if plot_info == 2 or plot_info == 3:
            # Goes through all data in cell.
            if xy_data[0] == "x":
                x_list.append(xy_data)
            if xy_data[0] == "y":
                y_list.append(xy_data)
    # Checks through each x_data item.
    xy_pairs = []
    xy_pairs_units = []
    if plot_info == 2 or plot_info == 3:
        for x_data in x_list:
            # Checks through each y data item.
            for y_data in y_list:
                # if the x and y data have the same source then they can be
                # plotted together
                if x_data[2] == y_data[2]:
                    # Appends which x values and y values that can be plotted
                    # against each other.
                    xy_pairs.append([x_data[1], y_data[1]])

    if plot_info == 1 and x[0] == 'Longitude' and y[0] == 'Latitude' and map_modules_imported is True:
        # Plots a map behind latitude and longitude data.
        plt.rcParams["figure.figsize"] = (15, 15)
        # Assigns data to variables
        lat = y[2]
        long = x[2]
        # Plots map with data
        backplt_map(lat, long, z_var=plot_data_map, text_title=title_text, z_var_limits=map_info_limits)
        backplt_map(lat, long, z_var=plot_data_map, scale_factor=(1 / scale), text_title=title_text,
                    z_var_limits=map_info_limits)
        return

    elif plot_info == 1 and x[0] == 'Longitude' and y[0] == 'Latitude' and map_modules_imported is False:
        # Print the following if the map modules are not installed.
        print('Backplotting map modules not installed. Check that geopandas, '
              + 'contextily and pyproj are installed correctly for this '
              + 'feature. Information on installing these packages can be '
              + 'found on: \n'
              + 'https://autoflpy.readthedocs.io/en/latest/installation.html')
        # Allows for custom title to be used:
        if title_text is not None:
            title = str(title_text)
        else:
            title = "Latitude v Longitude"
    elif plot_info == 1:
        plt.plot(x[2], y[2])
        # plots x name with unit in brackets.
        plt.xlabel(x[0] + " (" + x[1] + ")")
        xlabel = x[0]  # used for checking if the xlabel is time
        # plots y name with unit in brackets.
        plt.ylabel(y[0] + " (" + y[1] + ")")
        # plots title for graph.
        if title_text is not None:
            title = str(title_text)
        else:
            title = y[0] + " v " + x[0]
    # If y units have the same unit then this will format the graphs as
    # required.
    if plot_info == 2:
        for pair in xy_pairs:
            if pair[1][0][:4] == "Vibe":
                # plots log y values for vibration data.
                plt.semilogy(pair[0][2], pair[1][2], label=pair[1][0])
            else:
                # plots x against y values.
                plt.plot(pair[0][2], pair[1][2], label=pair[1][0])
        # Puts in first item.
        text = xy_pairs[0][1][0]
        for pair in xy_pairs[1:-1]:
            text += ", " + pair[1][0]
        # Adds and to end of text
        text += " and " + xy_pairs[len(xy_pairs) - 1][1][0]
        # Plots Legend.
        plt.legend()
        # Plots Y label.
        plt.ylabel(text + " (" + xy_pairs[0][1][1] + ")")
        # Plots X label.
        plt.xlabel(xy_pairs[0][0][0] + " (" + xy_pairs[0][0][1] + ")")
        xlabel = xy_pairs[0][0][0]  # used for checking if the xlabel is time
        # Plots the title.
        if title_text is not None:
            title = str(title_text)
        else:
            title = text + " v " + xy_pairs[0][0][0]
    # If y units do not have the same unit then this will format the graphs
    # as required.
    if plot_info == 3:
        for pair in xy_pairs:
            # plots x against y values.
            plt.plot(pair[0][2], pair[1][2], label=pair[1][0] + " (" + pair[1][1] + ")")
        # Puts in first item.
        text = xy_pairs[0][1][0]
        for pair in xy_pairs[1:-1]:
            text += ", " + pair[1][0]
        # Adds and to end of text
        text += " and " + xy_pairs[len(xy_pairs) - 1][1][0]
        # Plots Legend.
        plt.legend()
        # Plots X label.
        plt.xlabel(xy_pairs[0][0][0] + " (" + xy_pairs[0][0][1] + ")")
        xlabel = xy_pairs[0][0][0]  # used for checking if the xlabel is time
        # Plots the title.
        if title_text is not None:
            title = str(title_text)
        else:
            title = text + " v " + xy_pairs[0][0][0]
    # if plot info is equal to 0 then nothing is returned
    if plot_info == 0:
        print('No data present or variables entered incorrectly.')
        return
    # Splits title if its width exceeds 60
    wrapped_title = textwrap.wrap(title, width=60)
    # Creates an empty string for the final title
    final_title = ""
    # Goes through each line in the title and joins them together with a new
    # line character between each line.
    for title_line in wrapped_title:
        final_title += title_line + "\n"
    # Removes new line at end
    plt.title(final_title[:-1], y=1.05)
    # Checks to see if plot limits have been set for the x values
    if isinstance(x_limits[0], int) and isinstance(x_limits[1], int):
        plt.xlim(x_limits)
    # Checks to see if plot limits have been set for the y values
    if isinstance(y_limits[0], int) and isinstance(y_limits[1], int):
        plt.ylim(y_limits)

    axes_limits_center_y = (plt.gca().get_ylim()[0] + plt.gca().get_ylim()[1]) / 2
    axes_limits_x = [plt.gca().get_xlim()[0], plt.gca().get_xlim()[1]]
    if arm_data is True:
        arm_times = []
        disarm_times = []
        for event in range(len(arm_plot_data[0][2])):
            # arm_plot_data[0][2] is the list of events that occurred in the flight.
            if str(arm_plot_data[0][2][event]) == "10":
                # 10 is the event that signifies that the drone is armed
                arm_times.append(arm_plot_data[1][2][event])
                # arm_plot_data[1][2] = times associated with the events.
            if str(arm_plot_data[0][2][event]) == "11":
                # 11 is the event that signifies that the drone is disarmed
                disarm_times.append(arm_plot_data[1][2][event])
                # arm_plot_data[1][2] = times associated with the events.

        for times in arm_times:
            # Plot the arm events:
            plt.axvline(times, color="g")
            plt.annotate("ARM", [times, axes_limits_center_y])
        for times in disarm_times:
            # Plot the disarm events:
            plt.axvline(times, color="r")
            plt.annotate("DISARM", [times, axes_limits_center_y])
        # Prints time armed:
        for section in range(len(arm_times)):
            try:
                print("Time armed: ", round(disarm_times[section] - arm_times[section], 2), "s")
            except IndexError:
                continue

    # For adding global markers across all figures.
    if xlabel is not None and xlabel == "Time":
        for marker in marker_list:
            # Only plots marker if it is in the correct range
            if axes_limits_x[0] < marker < axes_limits_x[1]:
                if type(marker) is float or type(marker) is int:
                    # Plots the markers
                    plt.axvline(marker, color="k")
                    plt.annotate(marker, [marker, axes_limits_center_y])

    plt.grid(which='both', axis='both', linewidth=0.2, color="0.1")
    plt.show()


def multiaxis_graph_plotter(plot_information_left, plot_information_right,
                            values_list, x_limits=("x_min", "x_max"),
                            y_limits_left=("y_min", "y_max"),
                            y_limits_right=("y_min", "y_max"), marker_list=(),
                            legend_location=1, arm_data=False,
                            title_text=None):
    """ Goes through graph data, finds source and gets required data from
    values. plot information structure, [x, name, data_source], plots data on
    left and right axis as specified as inputs, legend location will specify
    where the legend should go.

    arm_data is an additional function to display when the UAV was armed/disarmed. This works if the EV (Event) data
    is has been recorded and is present in the Data_sources.txt document.

    title_text allows the user to give figures custom titles in the form of a string.
    """

    # TODO: KEEP AN EYE ON THESE:
    text = None
    title = None
    x = None
    y = None
    reference_y_unit = None
    reference_x_unit = None
    reference_x_heading = None
    arm_plot_data = None
    xlabel = None

    # List of data to plot returns plot data which has structure:
    # [axis, [data_source, column]]
    plot_information = [plot_information_left, plot_information_right]
    plot_list = []
    plt.rcParams["figure.figsize"] = (15, 3)

    if arm_data is True:
        # Imports data for the arming/disarming if it is present.
        arm_info = [["id", "ev"], ["time", "ev"]]
        arm_plot_data = []
        index = []
        for index in arm_info:
            values_list_index = 0
            # sets value_found to a default of False
            # Checks to see if the 'data source' recorded in the graph list
            # matches the 'data sources' in the list structure values_list.
            for values_list_data in values_list:
                # Finds data source.
                if index[1] == values_list_data[0].lower():
                    index.append(values_list_index)
                    # Finds corresponding time source.
                    # Goes through each column searching for a match.
                    for column in values_list[values_list_index][1:]:
                        # Checks to see if they have the same title.
                        if column[0].lower() == index[0]:
                            # if they do then the data is appended.
                            arm_plot_data.append(column)
                            # exits for loop if data has been appended.
                            break
                values_list_index += 1
    if arm_data is True:
        if len(arm_plot_data) != 0:
            arm_data = True
        else:
            # Data has not been imported properly or is not present.
            print("Arm data is not present or has not been imported properly. Make sure \"EV\" is present in the "
                  "Data_sources.txt file, then run autoflpy again to re-generate the data.")
            # Sets arm_data to false.
            arm_data = False

    # Goes through all the elements in the left list
    for element in plot_information_left:
        # If the element contains an x value and is not already in the right
        # list then it is appended to this list
        if element[0] == "x" and element not in plot_information_right:
            plot_information_right.append(element)
    # Goes through all the elements in the right list
    for element in plot_information_right:
        # If the element contains an x value and is not already in the left
        # list then it is appended to this list
        if element[0] == "x" and element not in plot_information_left:
            plot_information_left.append(element)
    for information in plot_information:
        plot_data = []
        for data in information:
            values_list_index = 0
            # sets value_found to a default of False
            # Checks to see if the 'data source' recorded in the graph list
            # matches the 'data sources' in the list structure values_list.
            for values_list_data in values_list:
                # Finds data source.
                if data[2] == values_list_data[0].lower():
                    data.append(values_list_index)
                    # Goes through each column searching for a match.
                    for column in values_list[values_list_index][1:]:
                        # Checks to see if they have the same title.
                        if column[0].lower() == data[1]:
                            # if they do then the data is appended.
                            plot_data.append([data[0], column, data[2]])
                            # exits for loop if data has been appended.
                            break
                values_list_index += 1

        # Goes through the graph list and finds the matching values in the
        # values_list and then appends these values to a new list with x or y
        # stated. Returns plot data which has structure:
        # [axis, [data_source, column]] This will go through all the data and
        # plot it. Plot info is used to inform the code what graph style that
        # it needs to plot. A final plot info of 0 means that the combination
        # of x and y values is invalid and so the cell will be automatically
        # removed. A final plot info of 1 means that there is just x and y,
        # a final plot info of 2 means that there are n x values which must
        # have the same name and unit (ie be the same information as the first
        # x but from a different data source) and multiple y values with the
        # same unit. A final plot info of 3 means that there are multiple y
        # values which do not have the same unit and n x values which must have
        # the same name and unit.
        plot_info = 0
        # checks the length of the cell, if there is one x and y value to
        # plot
        if len(plot_data) == 2:
            plot_info = 1
        if len(plot_data) > 2:
            plot_info = 2
        # Used to count the number of Xs
        x_count = 0
        for xy in plot_data:
            if xy[0] == "x":
                x_count += 1
        # if x count equals to 0 then plot info is set to 0
        if x_count == 0:
            plot_info = 0
        # If all the values are x's then plot info must be 0.
        if x_count == len(plot_data):
            plot_info = 0
        # If there is more than 1 x value
        if x_count > 1:
            first_x_unit = True
            if plot_info == 2:
                # Check through the cells that contain x.
                for xy_data in plot_data:
                    if xy_data[0] == "x":
                        # Check if this is the first x value unit that has been
                        # evaluated.
                        if first_x_unit is True:
                            # If it is then it sets it to be the reference unit
                            reference_x_unit = xy_data[1][1]
                            # Sets a reference heading for the x data.
                            reference_x_heading = xy_data[1][0]
                            first_x_unit = False
                        else:
                            # Sets the unit of the next item
                            unit = xy_data[1][1]
                            # Sets the heading of the next item
                            heading = xy_data[1][0]
                            if reference_x_unit == unit and reference_x_heading == heading:
                                plot_info = 2
                            else:
                                # Removes graph if the x values provided have
                                # different units.
                                plot_info = 0
                                break
            else:
                # If there are two variables (plot info = 1) and both variables
                # are x variables then do not plot the data.
                plot_info = 0
        # Sets first unit to True, so that the reference values are recorded
        # when the first lot of y data arrives.
        first_y_unit = True
        # If there is more than 1 y value
        if plot_info == 2:
            # Check through the cells that contain y.
            for xy_data in plot_data:
                if xy_data[0] == "y":
                    # Check if this is the first unit
                    if first_y_unit is True:
                        # If it is then it sets it to be the reference unit.
                        reference_y_unit = xy_data[1][1]
                        first_y_unit = False
                    else:
                        # If this is the second y value found.
                        unit = xy_data[1][1]
                        # If the units are constant then plot them together
                        if reference_y_unit == unit:
                            plot_info = 2
                        else:
                            plot_info = 3
                            break
        # Appends data to list
        plot_list.append([plot_info, plot_data])
    # Plots data
    graph, axis_1 = plt.subplots()
    # Renames data to make it compatible with older code.
    plot_info = plot_list[0][0]
    plot_data = plot_list[0][1]
    # Counts how many lines are being drawn.
    line_count = 0
    # Creates a list with a label in it for the axis.
    lines = axis_1.plot([], [], " ", label="Left axis")
    # Counts number of x.
    x_list = []
    # Counts number of y.
    y_list = []

    for xy_data in plot_data:
        # Checks to see what plot info equals.
        if plot_info == 1:
            # Checks to see if the current data being viewed is y data
            if xy_data[0] == "x":
                x = xy_data[1]
            # Checks to see if the data being viewed is x data.
            if xy_data[0] == "y":
                y = xy_data[1]
        # Goes through all data in cell.
        if xy_data[0] == "x":
            x_list.append(xy_data)
        if xy_data[0] == "y":
            y_list.append(xy_data)
    # Checks through each x_data item.
    xy_pairs = []
    for x_data in x_list:
        # Checks through each y data item.
        for y_data in y_list:
            # if the x and y data have the same source then they can be
            # plotted together
            if x_data[2] == y_data[2]:
                # Appends which x values and y values that can be plotted
                # against each other.
                xy_pairs.append([x_data[1], y_data[1]])
    if plot_info == 1:
        line = axis_1.plot(x[2], y[2], label=y[0],
                           color="C" + str(line_count))
        # plots x name with unit in brackets.
        axis_1.set_xlabel(x[0] + " (" + x[1] + ")")
        xlabel = x[0]  # For determining if the x axis is time.
        # plots y name with unit in brackets.
        axis_1.set_ylabel(y[0] + " (" + y[1] + ")")
        # plots title for graph.
        title = y[0]
        line_count = 1
        lines += line

    # If y units have the same unit then this will format the graphs as
    # required.
    if plot_info == 2:
        for pair in xy_pairs:
            # plots x against y values.
            line = axis_1.plot(pair[0][2], pair[1][2], label=pair[1][0],
                               color="C" + str(line_count))
            # Increments line count
            line_count += 1
            # Appends current line to list of lines.
            lines += line
        # Puts in first item.
        text = xy_pairs[0][1][0]
        for pair in xy_pairs[1:-1]:
            text += ", " + pair[1][0]
        # Adds and to end of text
        if len(xy_pairs) != 1:
            text += ", " + xy_pairs[len(xy_pairs) - 1][1][0]
        # Plots Legend.
        # Plots Y label.
        axis_1.set_ylabel(text + " (" + xy_pairs[0][1][1] + ")")
        # Plots X label.
        axis_1.set_xlabel(xy_pairs[0][0][0] + " (" + xy_pairs[0][0][1] + ")")
        xlabel = xy_pairs[0][0][0]  # For determining if the x axis is time.
        # Plots the title.
        title = text

    # If y units do not have the same unit then this will format the graphs
    # as required.
    if plot_info == 3:
        for pair in xy_pairs:
            # plots x against y values.
            line = axis_1.plot(pair[0][2], pair[1][2], label=(pair[1][0] + " (" + pair[1][1] + ")"),
                               color="C" + str(line_count))
            # Increments line count
            line_count += 1
            # Appends current line to list of lines.
            lines += line
        # Puts in first item.
        text = xy_pairs[0][1][0]
        for pair in xy_pairs[1:-1]:
            text += ", " + pair[1][0]
        # Adds and to end of text
        if len(xy_pairs) != 1:
            text += ", " + xy_pairs[len(xy_pairs) - 1][1][0]
        # Plots X label.
        axis_1.set_xlabel(xy_pairs[0][0][0] + " (" + xy_pairs[0][0][1] + ")")
        xlabel = xy_pairs[0][0][0]  # For determining if the x axis is time.
        # Plots the title.
        title = text

    # Records plot info for the left axis
    plot_info_left = plot_info
    # Renames data to make it compatible with older code.
    plot_info = plot_list[1][0]
    plot_data = plot_list[1][1]
    axis_2 = axis_1.twinx()
    # If there is Y axis data for the Right hand axis then plot the label
    if plot_info != 0:
        lines += axis_2.plot([], [], " ", label="Right axis")
    # Counts number of x.
    x_list = []
    # Counts number of y.
    y_list = []
    for xy_data in plot_data:
        # Checks to see what plot info equals.
        if plot_info == 1:
            # Checks to see if the current data being viewed is y data
            if xy_data[0] == "x":
                x = xy_data[1]
            # Checks to see if the data being viewed is x data.
            if xy_data[0] == "y":
                y = xy_data[1]
        # Goes through all data in cell.
        if xy_data[0] == "x":
            x_list.append(xy_data)
        if xy_data[0] == "y":
            y_list.append(xy_data)
    # Checks through each x_data item.
    xy_pairs = []
    for x_data in x_list:
        # Checks through each y data item.
        for y_data in y_list:
            # if the x and y data have the same source then they can be
            # plotted together
            if x_data[2] == y_data[2]:
                # Appends which x values and y values that can be plotted
                # against each other.
                xy_pairs.append([x_data[1], y_data[1]])
    if plot_info == 1:
        line = axis_2.plot(x[2], y[2], label=y[0],
                           color="C" + str(line_count))
        # Increments line count
        line_count += 1
        # Appends current line to list of lines.
        lines += line
        # plots y name with unit in brackets.
        axis_2.set_ylabel(y[0] + " (" + y[1] + ")")
        # plots title for graph.
        text = y[0] + " v " + x[0]
        xlabel = x[0]  # For determining if the x axis is time.
    # If y units have the same unit then this will format the graphs as
    # required.
    if plot_info == 2:
        for pair in xy_pairs:
            # plots x against y values.
            line = plt.plot(pair[0][2], pair[1][2], label=pair[1][0],
                            color="C" + str(line_count))
            # Increments line count
            line_count += 1
            # Appends current line to list of lines.
            lines += line
        # Puts in first item.
        text = xy_pairs[0][1][0]
        for pair in xy_pairs[1:-1]:
            text += ", " + pair[1][0]
        # Adds and to end of text
        if len(xy_pairs) != 1:
            text += ", " + xy_pairs[len(xy_pairs) - 1][1][0]
        # Plots Y label.
        axis_2.set_ylabel(text + " (" + xy_pairs[0][1][1] + ")")
        # Plots X label.
        axis_2.set_xlabel(xy_pairs[0][0][0] + " (" + xy_pairs[0][0][1] + ")")
        xlabel = xy_pairs[0][0][0]  # For determining if the x axis is time.
        # Adds the x variable for use in the title
        text += " v " + xy_pairs[0][0][0]
    # If y units do not have the same unit then this will format the graphs
    # as required.
    if plot_info == 3:
        for pair in xy_pairs:
            # plots x against y values.
            line = axis_2.plot(pair[0][2], pair[1][2], label=(pair[1][0] + " (" + pair[1][1] + ")"),
                               color="C" + str(line_count))
            # Increments line count
            line_count += 1
            # Appends current line to list of lines.
            lines += line
        # Puts in first item.
        text = xy_pairs[0][1][0]
        for pair in xy_pairs[1:-1]:
            text += ", " + pair[1][0]
        # Adds and to end of text
        if len(xy_pairs) != 1:
            text += ", " + xy_pairs[len(xy_pairs) - 1][1][0] + " v " + xy_pairs[len(xy_pairs) - 1][0][0]
        # Plots X label.
        axis_2.set_xlabel(xy_pairs[0][0][0] + " (" + xy_pairs[0][0][1] + ")")
        xlabel = xy_pairs[0][0][0]  # For determining if the x axis is time.
    # If there is no valid data then return nothing.
    if plot_info == 0 and plot_info_left == 0:
        plt.close()
        print('No data present or data entered incorrectly.')
        return
    if plot_info != 0 and plot_info_left != 0:
        # Plots the title.
        full_title = title + " and " + text

    elif plot_info == 0:
        # Plots the title.
        full_title = title
        # Hides right axis if data is missing.
        axis_2.set_yticks([])
    else:
        # Creates a title.
        full_title = text + " v " + \
                     xy_pairs[0][0][0]
        # Hides left axis if data is missing.
        axis_1.set_yticks([])
        print('Left axis data missing or entered incorrectly.')

    # Plots a custom title if specified:
    if title_text is not None:
        full_title = str(title_text)

    # Splits title if its width exceeds 60
    wrapped_title = textwrap.wrap(full_title, width=60)
    # Creates an empty string for the final title
    final_title = ""
    # Goes through the title and joins them together with a new
    # line character between each line.
    for title_line in wrapped_title:
        final_title += title_line + "\n"
    # Removes new line at end
    plt.title(final_title[:-1], y=1.05)
    # Creates a blank list for the labels.
    label = []
    # Goes through each of the lines and adds them to a list.
    for plotted_line in lines:
        label.append(plotted_line.get_label())
    # Plots labels if both axes are valid.
    if plot_info != 0:
        # Plots legends so that it is always in the top right of the graph.
        axis_2.legend(lines, label, loc=legend_location)
    else:
        # Removes left axis label from legend if left hand axis is not
        # plotting.
        axis_2.legend(lines[1:], label[1:], loc=legend_location)
        print('Right axis data missing or entered incorrectly.')

    # Checks to see if plot limits have been set for the x values
    if isinstance(x_limits[0], int) and isinstance(x_limits[1], int):
        axis_1.set_xlim(x_limits)
    # Checks to see if plot limits have been set for the y values on the left
    # axis.
    if isinstance(y_limits_left[0], int) and isinstance(y_limits_left[1], int):
        axis_1.set_ylim(y_limits_left)
        # Checks to see if plot limits have been set for the y values on the
        # right axis.
    if isinstance(y_limits_right[0], int) and isinstance(y_limits_right[1], int):
        axis_2.set_ylim(y_limits_right)

    axes_limits_center_y = (plt.gca().get_ylim()[0] + plt.gca().get_ylim()[1]) / 2
    axes_limits_x = [plt.gca().get_xlim()[0], plt.gca().get_xlim()[1]]
    if arm_data is True:
        arm_times = []
        disarm_times = []
        for event in range(len(arm_plot_data[0][2])):
            # arm_plot_data[0][2] is the list of events that occurred in the flight.
            if str(arm_plot_data[0][2][event]) == "10":
                # 10 is the event that signifies that the drone is armed
                arm_times.append(arm_plot_data[1][2][event])
                # arm_plot_data[1][2] = times associated with the events.
            if str(arm_plot_data[0][2][event]) == "11":
                # 11 is the event that signifies that the drone is disarmed
                disarm_times.append(arm_plot_data[1][2][event])
                # arm_plot_data[1][2] = times associated with the events.

        for times in arm_times:
            # Plot the arm events:
            plt.axvline(times, color="g")
            plt.annotate("ARM", [times, axes_limits_center_y])
        for times in disarm_times:
            # Plot the disarm events:
            plt.axvline(times, color="r")
            plt.annotate("DISARM", [times, axes_limits_center_y])
        # Prints time armed:
        for section in range(len(arm_times)):
            try:
                print("Time armed: ", round(disarm_times[section] - arm_times[section], 2), "s")
            except IndexError:
                continue

    # For adding global markers across all figures.
    if xlabel is not None and xlabel == "Time":
        for marker in marker_list:
            # Plots only the markers in the correct range.
            if axes_limits_x[0] < marker < axes_limits_x[1]:
                if type(marker) is float or type(marker) is int:
                    # Plots the markers
                    plt.axvline(marker, color="k")
                    plt.annotate(marker, [marker, axes_limits_center_y])

    plt.grid(which='both', axis='both', linewidth=0.2, color="0.1")
    plt.show()


def backplt_map(lat, long, z_var, scale_factor=1, text_title=None, z_var_limits=(None, None)):
    """
    This plots a map behind some latitude-longitude data and colours the line according to a third variable (z_var).

    """

    # Sets titles for the data frame
    column_titles = np.array(['index', 'lat, long'])
    index = range(len(lat))
    points = []
    # Formats the location data in the correct way to make the data frame
    for point in range(len(lat)):
        points.append([long[point], lat[point]])
    # Creates a correctly formatted numpy array
    path_data_array = (np.array([index, points])).T
    # Turns this array into a pandas data frame
    path_data = pd.DataFrame(path_data_array,
                             columns=column_titles)
    # Creates a GeoDataFrame to be used with the map and sets the geometry
    # and coordinate system (epsg 4326) - latitude and longitude
    geo_data_frame = gpd.GeoDataFrame(
        path_data,
        geometry=gpd.points_from_xy(long, lat),
        crs={'init': 'epsg:4326'})
    # Renames the GeoDataFrame
    path_data_geo = geo_data_frame
    # Changes the data's coordinate system to epsg 3857 (needed for the
    # maps)
    path_data_geo = path_data_geo.to_crs(epsg=3857)

    # To get the axis labels correctly:
    # Find max and min lat and long.
    in_proj = proj(init='epsg:4326')
    out_proj = proj(init='epsg:3857')

    # Finds the centre point of the plot
    centre_pnt = [(max(lat) + min(lat)) / 2., (max(long) + min(long)) / 2.]
    # Finds distances to the corner points from the center point
    corner_dist = [max(lat) - centre_pnt[0], min(lat) - centre_pnt[0],
                   max(long) - centre_pnt[1], min(long) - centre_pnt[1]]

    # Assigns and scales corner distances of the plot
    extreme_lat = [centre_pnt[0] + corner_dist[0] * scale_factor,
                   centre_pnt[0] + corner_dist[1] * scale_factor]
    extreme_long = [centre_pnt[1] + corner_dist[2] * scale_factor,
                    centre_pnt[1] + corner_dist[3] * scale_factor]
    fig, ax = plt.subplots(1, 1)

    # Retrieves data from the dataframe
    geometry_data = [path_data_geo['geometry'].x,
                     path_data_geo['geometry'].y]

    # Processes data for the colour scale:
    # Interpolates the data for the colour series over the data's time scale
    # z_var[1][2] = colour variable time data
    # z_var[0][2] = colour variable data
    z_var_interp = interp.interp1d(z_var[1][2], z_var[0][2])

    # Creates the data series of same length as the latitude/longitude data:
    # z_var[2][2] = gps time data
    colour_data_uncut = []
    for point in [p for p in z_var[2][2] if min(z_var[1][2]) <= p <= max(z_var[1][2])]:
        colour_data_uncut.append(z_var_interp(point))

    # TODO: THIS NEEDS FIXING IN A WAY THAT WORKS BETTER. NEED TO MATCH THE TIME STAMPS OF THE LOCATION DATA WITH
    #  THE COLOUR DATA.
    # Makes sure that the colour data has the same length as the latitude and longitude data
    colour_data = []
    if len(geometry_data[0]) != len(colour_data_uncut):
        for point in colour_data_uncut[:(len(geometry_data) - 1)]:
            colour_data.append(point)
    else:
        colour_data = colour_data_uncut

    # Creates lists of points of latitude and longitude of colour values above and below the limits specified limits
    # and notes the points
    low_colour_lat_values = []
    low_colour_long_values = []

    high_colour_lat_values = []
    high_colour_long_values = []

    try:
        lower_limit = z_var_limits[0]
        upper_limit = z_var_limits[1]
    except IndexError:
        print("Limits not entered in the correct format. Format should be [lower_limit, upper_limit] where lower_limit "
              "and upper_limit are floats or integers.")
        lower_limit = None
        upper_limit = None

    # Checks that the formats are correct for the lower_ and upper_limit(s)
    if type(lower_limit) is str or type(lower_limit) is float:
        print("Lower limit type not correct. Format should be [lower_limit, upper_limit] where lower_limit "
              "and upper_limit are floats or integers.")
        lower_limit = None
    if type(upper_limit) is str or type(upper_limit) is float:
        print("Upper limit type not correct. Format should be [lower_limit, upper_limit] where lower_limit "
              "and upper_limit are floats or integers.")
        upper_limit = None

    # Adds geometry data
    for index in range(len(colour_data)):
        if lower_limit is not None:
            if colour_data[index] <= lower_limit:
                low_colour_lat_values.append(geometry_data[0][index])
                low_colour_long_values.append(geometry_data[1][index])
        if upper_limit is not None:
            if colour_data[index] >= upper_limit:
                high_colour_lat_values.append(geometry_data[0][index])
                high_colour_long_values.append(geometry_data[1][index])

    if scale_factor <= 200:
        # Plots the geometry data using matplotlib
        plt.plot(geometry_data[0], geometry_data[1], 'r', zorder=1,
                 linewidth=0.5)
        # Plots the colour data over the base data
        mapplot = plt.scatter(geometry_data[0], geometry_data[1],
                              c=colour_data, marker='.',
                              cmap='gnuplot', zorder=2)
        # Plots lower and upper limit data if limits are present.
        if lower_limit is not None:
            plt.scatter(low_colour_lat_values, low_colour_long_values,
                        s=80, facecolors='none', edgecolors='b', marker='o', zorder=3)
        if upper_limit is not None:
            plt.scatter(high_colour_lat_values, high_colour_long_values,
                        s=80, facecolors='none', edgecolors='r', marker='o', zorder=4)

    else:
        # Plots a point symbolising the mean of the data.
        mapplot = plt.scatter(np.mean(geometry_data[0]),
                              np.mean(geometry_data[1]),
                              c='r', marker='o', s=100, zorder=2)

    # Round min down, round max up for the labels
    extreme_lat_rounded = [np.ceil(extreme_lat[0] * 1e3) / 1e3, np.floor(
        extreme_lat[1] * 1e3) / 1e3]
    extreme_long_rounded = [np.ceil(extreme_long[0] * 1e3) / 1e3, np.floor(
        extreme_long[1] * 1e3) / 1e3]

    # Transforms extreme x and y coordinates to the map reference frame
    trans_extreme_lat = [0, 0]
    trans_extreme_long = [0, 0]

    trans_extreme_long[0], trans_extreme_lat[0] = \
        transform(in_proj, out_proj, extreme_long_rounded[0],
                  extreme_lat_rounded[0])
    trans_extreme_long[1], trans_extreme_lat[1] = \
        transform(in_proj, out_proj, extreme_long_rounded[1],
                  extreme_lat_rounded[1])

    # Sets x and y limits from the corner points
    trans_height = trans_extreme_lat[0] - trans_extreme_lat[1]
    trans_width = trans_extreme_long[0] - trans_extreme_long[1]

    # Makes the map plot square by changing the corner distances to the
    # maximum values.
    trans_height = max(trans_height, trans_width)
    trans_width = trans_height

    # Finds the new center location. This is different to the previous center
    # due to the earth (round) being flattened.
    trans_centre = [(trans_extreme_lat[0] + trans_extreme_lat[1]) / 2,
                    (trans_extreme_long[0] + trans_extreme_long[1]) / 2]

    # Sets the limits for the axes.
    ax.set_xlim(trans_centre[1] - trans_width / 2,
                trans_centre[1] + trans_width / 2)
    ax.set_ylim(trans_centre[0] - trans_height / 2,
                trans_centre[0] + trans_height / 2)

    # Create intermediate points with linspace spaced at 6 increments.
    trans_lat_values = np.arange(trans_centre[0] - trans_height / 2,
                                 trans_centre[0] + trans_height / 2, (trans_height / 6))
    trans_long_values = np.linspace(trans_centre[1] - trans_width / 2,
                                    trans_centre[1] + trans_width / 2, len(trans_lat_values))

    # Convert to epsg3857 - from https://gis.stackexchange.com/questions/
    # 78838/converting-projected-coordinates-to-lat-lon-using-python
    long_values_4326, lat_values_4326 = transform(out_proj, in_proj,
                                                  trans_long_values, trans_lat_values)

    # Use xticks and yticks to replace with original values
    plt.xticks(trans_long_values, np.round(long_values_4326, 4))
    plt.yticks(trans_lat_values, np.round(lat_values_4326, 4))

    try:
        # Tries to plot a Statem terrain map
        ctx.add_basemap(ax, url=ctx.sources.ST_TERRAIN)
    except HTTPError:
        # If the resolution is not good enough, plots an OpenStreetMap
        # instead
        print('Location does not have high resolution Stamen terrain'
              ' map data. Defaulting to OpenStreetMap data.')
        ctx.add_basemap(ax, url=ctx.sources.OSM_A)
    except ConnectionError:
        # If there is no internet connection present, the map can't be called.
        print('Map unavailable when offline. Try again once an internet '
              'connection has been established.')
    # plots x name with unit in brackets.
    plt.xlabel('Longitude' + " (degrees)")
    # plots y name with unit in brackets.
    plt.ylabel('Latitude' + " (degrees)")
    # plots title for graph.
    map_title = "Latitude v Longitude"

    if text_title is not None:
        map_title = text_title
    elif scale_factor <= 5:
        map_title += " v " + str(z_var[0][0])

    # Splits title if its width exceeds 60
    wraped_title = textwrap.wrap(map_title, width=60)
    # Creates an empty string for the final title
    final_title = ""
    # Goes through each line in the title and joins them together with a
    # new line character between each line.
    for title_line in wraped_title:
        final_title += title_line + "\n"
    plt.title(final_title[:-1], y=1.05)
    plt.grid(which='both', axis='both', linewidth=0.2, color="0.1")
    # Adds a colour bar to a plot if the scale is not out of bounds.
    if scale_factor <= 5:
        # Formats location of the colour bar
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        # Plots the colour map
        cbar = plt.colorbar(mapplot, cax=cax)
        # Adds a label to the colour bar
        # z_var[0][0] = colour variable name
        # z_var[0][1] = colour variable units
        cbar.ax.set_ylabel(str(z_var[0][0]) + " (" + str(z_var[0][1]) + ")", rotation=90)

    plt.show()
    return


def take_off_graph(values_list, marker_list=(), take_off_time=None, arm_data=False, alt_sensitivity=0.3,
                   groundspeed_sensitivity=0.3):
    """Plots the main variables over the take-off range of the flight on a multi-axis plot.

    Variables plotted:
    ["altitude", "baro"]
    ["groundspeed", "gps"]

    ["airspeed", "arsp"]
    ["aoa", "aoa"]

    ["pitch", "ctun"]
    ["desired pitch", "att"]

    ["throttle ch3", "rcin"]
    ["flap ch5", "rcin"]
    ["elevator ch2", "rcin"]
    ["current", "bat"]

    ["vibex", "vibe"]
    ["vibey", "vibe"]
    ["vibez", "vibe"]
    """
    take_off_time_calculated = False

    # TODO: Create a function to automatically tune the sensitivity - start high and reduce it until it doesn't make
    #  sense anymore.

    take_off_time_alt, take_off_groundspeed, take_off_time_spd = \
        take_off_detection.take_off_point_finder(values_list, alt_sensitivity=alt_sensitivity,
                                                 groundspeed_sensitivity=groundspeed_sensitivity)

    if take_off_time is None:
        take_off_time = take_off_time_alt
        take_off_time_calculated = True

    # Prints calculated times
    if take_off_time_calculated is True:
        print("Detected take-off time: ", take_off_time)
        if take_off_groundspeed is not None:
            print("Groundspeed at detected take-off: ", take_off_groundspeed)
        if take_off_time_spd is not None:
            print("Detected ground run start time: ", take_off_time_spd)

    # Sets bounds to display on the time axis
    lower_bound = int(float(take_off_time) - 10)
    upper_bound = int(float(take_off_time) + 15)

    # Sets the range for all of the graphs.
    x_limits = [lower_bound, upper_bound]
    y_limits_left = ["y_min", "y_max"]
    y_limits_right = ["y_min", "y_max"]
    y_limits = ["y_min", "y_max"]
    legend_location = 1

    # Plots data mentioned above.
    multiaxis_graph_plotter([["y", "altitude", "baro"], ["x", "time", "baro"]],
                            [["y", "groundspeed", "gps"], ["x", "time", "gps"]], values_list, x_limits, y_limits_left,
                            y_limits_right, marker_list, legend_location, arm_data=arm_data)

    multiaxis_graph_plotter([["y", "airspeed", "arsp"], ["x", "time", "arsp"]],
                            [["y", "aoa", "aoa"], ["x", "time", "aoa"]], values_list, x_limits, y_limits_left,
                            y_limits_right, marker_list, legend_location, arm_data=arm_data)

    graph_plotter([["y", "pitch", "att"], ["y", "desired pitch", "att"], ["x", "time", "att"]], values_list, x_limits,
                  y_limits, marker_list, arm_data=arm_data)

    multiaxis_graph_plotter([["y", "throttle ch3", "rcin"], ["y", "flap ch5", "rcin"], ["y", "elevator ch2", "rcin"],
                             ["x", "time", "rcin"]], [["y", "current", "bat"], ["x", "time", "bat"]],
                            values_list, x_limits, y_limits_left, y_limits_right, marker_list,
                            legend_location, arm_data=arm_data)

    graph_plotter([["x", "time", "vibe"], ["y", "vibex", "vibe"], ["y", "vibey", "vibe"], ["y", "vibez", "vibe"]],
                  values_list, x_limits, y_limits, marker_list, arm_data=arm_data)
