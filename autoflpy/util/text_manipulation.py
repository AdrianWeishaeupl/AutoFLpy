import os


def contents_opener(file_path, file_name):
    """This code opens a specified file and returns the contents"""
    # opens file
    file = open(file_path + os.sep + file_name, "r")
    # Extracts contents.
    contents = file.read()
    # Closes the file.
    file.close()
    return contents


def flight_log_graph_contents_replacer(contents):
    """Values list is from the function flight_data_and_axis."""
    comma = None
    lines = contents.split("\n")
    line_list = []
    # Finds the line numbers that contain the graph key word
    for index in range(len(lines)):
        if "\"GRAPH\\n\"" in lines[index]:
            line_list.append(index)
    # Creates a blank graph to be filled with data
    graph_data = []
    for index in line_list:
        a = 0
        # Step size
        b = 1
        # Creates a list for storing the index of the lines.
        local_graph_data = [index]
        # Creates an infinite loop used to find the end of that particular
        # cell in the notebook.
        while a == 0:
            # Checks through to see if lines no longer contain useful
            # information
            if lines[index + b] == "   ]":
                graph_data.append(local_graph_data)
                break
            # checks to see if the line is not just a gap
            if lines[index + b] != "    \"\\n\",":
                local_graph_data.append(index + b)
            # Increments b by 2.
            b += 1
    # Creates an empty graph to be filled with graph properties.
    graph_list = []
    # Creates an index for the graph data
    graph_data_index = 0
    # Goes through all of the items in the list graph data
    for data in graph_data:
        graph_list.append([])
        # Goes through each of the sub lists in the list graph_data and
        # processes the data
        for index in data[1:]:
            # Sets line to equal the line at that particular index.
            line = lines[index]
            # Removes gap at front of line
            line = line.replace("    \"", "")
            # Removes speech marks
            line = line.replace("\"", "")
            # Removes \n, from end
            line = line.replace("\\n,", "")
            # Makes line lowercase
            line = line.lower()
            # replace spaces with speech marks for jupyter
            line = line.replace(" ", "\\\", \\\"")
            # If the name has more than one word in it then replace the
            # underscore with a space.
            line = line.replace("_", " ")
            # Appends data to list.
            graph_list[graph_data_index].append("[\\\"" + line + "\\\"]")
        graph_data_index += 1
    notebook_lines = []
    for data in graph_list:
        line = "  {\n   \"cell_type\": \"code\",\n" + \
               "   \"execution_count\": null,\n   \"metadata\": {},\n" + \
               "   \"outputs\": [],\n   \"source\": [\n" + \
               "   \"x_limits=[\\\"x_min\\\", \\\"x_max\\\"]\\n\",\n" + \
               "   \"y_limits=[\\\"y_min\\\", \\\"y_max\\\"]\\n\",\n" + \
               "   \"graph_plotter(["
        for axis in data:
            line += axis + ", "
        line = line[:-2]
        line += "], values_list, x_limits, y_limits, marker_list)\"\n   ]\n  }"
        notebook_lines.append(line)
    # Goes through each element in the line list
    index = 0
    for element in line_list:
        # Creates empty string for text.
        old_cell_text = ""
        # Goes backwards though lines appending text until it reaches the start
        # of the cell.
        for lines_before in reversed(lines[:element]):
            a = 0
            old_cell_text = lines_before + "\n" + old_cell_text
            if lines_before == "  {":
                a = 1
                # Finds the end line of the list appending text along the way,
                # if the line contains "  }" or "  },"then then the code stops
                # appending lines.
                for lines_after in lines[element:]:
                    if "  }," in lines_after:
                        old_cell_text = old_cell_text + "  },\n"
                        comma = True
                        break
                    else:
                        if "  }" in lines_after:
                            old_cell_text = old_cell_text + "  }\n"
                            comma = False
                            break
                        else:
                            old_cell_text = old_cell_text + lines_after + "\n"
            if a == 1:
                break
        # Adds comma to end if required
        if comma is not None and comma is True:
            end = ",\n"
        else:
            end = "\n"
        # Replaces existing text with graphs
        contents = contents.replace(old_cell_text, notebook_lines[index] + end)
        # increments the index so that the next set of data is included.
        index += 1
    return contents


def flight_log_multiaxis_graph_contents_replacer(contents):
    """Values list is from the function flight_data_and_axis."""
    comma = None

    lines = contents.split("\n")
    line_list = []
    # Finds the line numbers that contain the graph key word
    for index in range(len(lines)):
        if "\"MULTIAXIS_GRAPH\\n\"" in lines[index]:
            line_list.append(index)
    # Creates a blank graph to be filled with data
    graph_data = []
    for index in line_list:
        a = 0
        # Step size
        b = 1
        # Creates a list for storing the index of the lines.
        local_graph_data = [index]
        # Creates an infinite loop used to find the end of that particular cell
        # in the notebook.
        while a == 0:
            # Checks through to see if lines no longer contain useful
            # information
            if lines[index + b] == "   ]":
                graph_data.append(local_graph_data)
                break
            # checks to see if the line is not just a gap
            if lines[index + b] != "    \"\\n\",":
                local_graph_data.append(index + b)
            # Increments b by 2.
            b += 1
    # Creates an empty graph to be filled with graph properties.
    graph_list = []
    # Creates an index for the graph data
    graph_data_index = 0
    # Goes through all of the items in the list graph data
    for data in graph_data:
        graph_list.append([[], []])
        # sets axis to be 0 so it represents the left axis.
        axis = 0
        # Goes through each of the sub lists in the list graph_data and
        # processes the data
        for index in data[1:]:
            ignore = False
            # Sets line to equal the line at that particular index.
            line = lines[index]
            # Removes gap at front of line
            line = line.replace("    \"", "")
            # Removes speech marks
            line = line.replace("\"", "")
            # Removes \n, from end
            line = line.replace("\\n,", "")
            # Makes line lowercase
            if line == "LEFT_AXIS":
                axis = 0
                ignore = True
            if line == "RIGHT_AXIS":
                axis = 1
                ignore = True
            line = line.lower()
            # replace spaces with speech marks for jupyter
            line = line.replace(" ", "\\\", \\\"")
            # If the name has more than one word in it then replace the
            # underscore with a space.
            line = line.replace("_", " ")
            # Appends data to list if it is not set to ignore that row.
            if ignore is False:
                graph_list[graph_data_index][axis].append("[\\\"" + line
                                                          + "\\\"]")
        graph_data_index += 1
    notebook_lines = []
    for data in graph_list:
        line = "  {\n   \"cell_type\": \"code\",\n" + \
               "   \"execution_count\": null,\n   \"metadata\": {},\n" + \
               "   \"outputs\": [],\n   \"source\": [\n" + \
               "   \"x_limits=[\\\"x_min\\\", \\\"x_max\\\"]\\n\",\n" + \
               "   \"y_limits_left=[\\\"y_min\\\", \\\"y_max\\\"]\\n\",\n" + \
               "   \"y_limits_right=[\\\"y_min\\\", \\\"y_max\\\"]\\n\",\n" + \
               "   \"legend_location=1\\n\",\n" + \
               "   \"multiaxis_graph_plotter(["
        # Inputs data for the left axis.
        for axis_left in data[0]:
            line += axis_left + ", "
        # Removes last comma and space
        line = line[:-2]
        line += "], ["
        # Inputs data for the right axis.
        for axis_right in data[1]:
            line += axis_right + ", "
        # Removes last comma and space.
        line = line[:-2]
        line += "], values_list, x_limits, y_limits_left, y_limits_right," + \
                " marker_list, legend_location)\"\n   ]\n  }"
        notebook_lines.append(line)
    # Goes through each element in the line list
    index = 0
    for element in line_list:
        # Creates empty string for text.
        old_cell_text = ""
        # Goes backwards though lines appending text until it reaches the start
        # of the cell.
        for lines_before in reversed(lines[:element]):
            a = 0
            old_cell_text = lines_before + "\n" + old_cell_text
            if lines_before == "  {":
                a = 1
                # Finds the end line of the list appending text along the way,
                # if the line contains "  }" or "  },"then then the code stops
                # appending lines.
                for lines_after in lines[element:]:
                    if "  }," in lines_after:
                        old_cell_text = old_cell_text + "  },\n"
                        comma = True
                        break
                    else:
                        if "  }" in lines_after:
                            old_cell_text = old_cell_text + "  }\n"
                            comma = False
                            break
                        else:
                            old_cell_text = old_cell_text + lines_after + "\n"
            if a == 1:
                break
        # Adds comma to end if required
        if comma is True:
            end = ",\n"
        else:
            end = "\n"
        # Replaces existing text with graphs
        contents = contents.replace(old_cell_text, notebook_lines[index] + end)
        # increments the index so that the next set of data is included.
        index += 1
    return contents


def cell_remover(contents, key):
    """This function will remove the cells that contain a specific key
    and ensure that the last cell has the correct comma at the end."""
    # splits contents into lines.
    lines = contents.split("\n")
    line_list = []
    # Finds the line numbers that contain the key word
    for index in range(len(lines)):
        if key in lines[index]:
            line_list.append(index)
    for element in line_list:
        # Creates empty string for text.
        old_cell_text = ""
        # Goes backwards though lines appending text until it reaches the start
        # of the cell.
        element_current = element
        for lines_before in reversed(lines[:element]):
            element_current += -1
            a = 0
            old_cell_text = lines_before + "\n" + old_cell_text
            if lines_before == "  {":
                a = 1
                # Finds the end line of the list appending text along the way,
                # if the line contains "  }" or "  },"then the code stops
                # appending lines.
                for lines_after in lines[element:]:
                    if "  }," in lines_after:
                        old_cell_text = old_cell_text + "  },\n"
                        break
                    else:
                        if "  }" in lines_after:
                            old_cell_text = old_cell_text + "  }\n"
                            break
                        else:
                            old_cell_text = old_cell_text + lines_after + "\n"
            if a == 1:
                break
        # Replaces cells containing the word graph with blank text
        contents = contents.replace(old_cell_text, "")
    lines = contents.split("\n")
    # Finds the line numbers that contain the kernel spec key word
    kernel_spec_index = None
    for index in range(len(lines)):
        if "\"kernelspec\": {" in lines[index]:
            kernel_spec_index = index
            # Ends check as it has found what is looking for
            break
    # Sets kernel_spec_text to contain nothing.
    kernel_spec_text = ""
    # Goes through the lines after the lines containing kernel_spec
    if kernel_spec_index is not None:
        for line in reversed(lines[:kernel_spec_index]):
            # If the last line is as it should be then return the contents.
            if line == "  }":
                break
            else:
                # If the end of the last cell contains a comma then it must be
                # removed.
                if line == "  },":
                    # Removes comma from the end of the last cell.
                    contents = contents.replace("  },\n" + kernel_spec_text,
                                                "  }\n" + kernel_spec_text)
                    # Once comma is removed then break out of the for loop and
                    # return the contents.
                    break
                else:
                    # If not at the end then more lines are appended.
                    kernel_spec_text = line + "\n" + kernel_spec_text
    # Returns the new contents.
    return contents


def line_remover(contents, key):
    """ This function will removes any lines that contain a specific key."""
    # splits contents into lines.
    lines = contents.split("\n")
    contents = ""
    # Finds the line that contain the graph key word
    for line in lines:
        # checks that key is not in line
        if key not in line:
            # if it is not then the line is appended.
            contents += line + "\n"
        else:
            # if the line does not have a comma at the end so it is the last
            # line then remove the comma from the previous line.
            if line[-1:] != ",":
                contents = contents[:-2]
    # Returns the new contents.
    return contents
