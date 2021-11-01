
import pandas as pd
import pickle as pk
import os
from openpyxl import load_workbook
from autoflpy.util.metar_processing import *
from autoflpy.util.text_manipulation import *


"""
Flight Report Generation Code.
This code takes flight data in the form of an .xlsx document (generated from a
.log file in log_to_xlsx.py) or a correctly formatted .csv and plots and
formats the data to be displayed using a template .ipynb file.

@author Adrian Weishaeupl
aw6g15@soton.ac.uk 2019

Based on work done by Samuel Pearson (sp1g18@soton.ac.uk) (06-08/2019)

"""

# Checks to see if os.sep is \\
if os.sep == "\\":
    # If it is then it sets the jupyter sep to be \\\\\\\\ eight slashes so \\
    jupyter_sep = "\\\\\\\\"
else:
    jupyter_sep = "/"


def flight_log_maker(template_file_path, template_file_name,
                     flight_log_file_path, flight_data_file_path,
                     flight_data_file_names, csv_flight_data_file_path,
                     csv_flight_data_names, flight_dates, flight_numbers,
                     flight_log_file_name_header, icao_airfields, start_times_hours,
                     end_times_hours, metar_file_path, weather_data_lists, runway_data_lists,
                     include_metar):
    """This code will edit a specified template and return the result that has
    been produced after the substitution of data into the template."""
    print('Starting Flight Log Maker')
    # Sets the number of flights for iterating through the data lists
    number_of_flights = len(flight_dates)

    # loads contents.
    contents = contents_opener(template_file_path, template_file_name)

    # Formats flight_dates into a string for insertion into template
    flight_dates_str = ""
    for flight in range(number_of_flights):
        flight_date = str(flight_dates[flight])
        flight_dates_str += flight_date[6:] + "/" + flight_date[4:6] + "/" + flight_date[:4] + " and "
    flight_dates_str = flight_dates_str[:-5]

    # Inserts the dates into the contents.
    contents = contents.replace("FLIGHT_DATE", flight_dates_str)

    # Formats flight_numbers into a string for insertion into template
    flight_numbers_str = ""
    for flight in range(number_of_flights):
        flight_numbers_str += str(flight_numbers[flight]) + ", "
    flight_numbers_str = flight_numbers_str[:-2]

    # Inserts the flight number into the contents.
    contents = contents.replace("FLIGHT_NUMBER", flight_numbers_str)
    compressed_data_file_name = ""
    # Checks to see whether there is graph data or csv data that can be
    # used to plot graphs by checking if the path exists and if the path has a
    # suitable length to that it is not just greater than 1.
    directories_present = []
    for flight in range(number_of_flights):
        if (os.path.exists(flight_data_file_path + os.sep + flight_data_file_names[flight])
            is True and
            len(flight_data_file_path + os.sep + flight_data_file_names[flight]) > 1) \
            or \
            (os.path.exists(csv_flight_data_file_path + os.sep +
                            csv_flight_data_names[flight]) is True and
             len(csv_flight_data_file_path + os.sep +
                 csv_flight_data_names[flight]) > 1):
            directories_present.append(True)
        else:
            directories_present.append(False)
        # Assigns file name based on excel data
        compressed_data_file_name += str(flight_data_file_names[flight])[:-5] + "-"  # [:-5] removes the ".xslx"
    compressed_data_file_name = compressed_data_file_name[:-1]  # [:-1] removes the last "-"

    if all(directories_present):  # If all are true, carry on.
        print('Importing xlsx data')
        # This replaces the file path with the necessary information
        contents = contents.replace("PYTHON_FILE_PATH", "\\\"" +
                                    os.getcwd().replace("\\", jupyter_sep) +
                                    "\\\"")
        # This replaces the graph text label
        contents = contents.replace("GRAPH_TEXT", "")
        # This replaces the graph data label
        contents = contents.replace("\\\"# GRAPH_DATA_IMPORT\n\\\",", "")
        # This removes the label stating that a line is a graph line.
        contents = contents.replace("GRAPH_LINE", "")
        # Includes interactive Graphs.
        contents = flight_log_multiaxis_graph_contents_replacer(contents)
        # Includes interactive Graphs.
        contents = flight_log_graph_contents_replacer(contents)
    else:
        # Removes the cell importing the graph data.
        contents = cell_remover(contents, "# GRAPH_DATA_IMPORT")
        # Removes the cells containing graph data.
        contents = cell_remover(contents, "\"MULTIAXIS_GRAPH\\n\"")
        # Removes the cells containing graph data.
        contents = cell_remover(contents, "\"GRAPH\\n\"")
        # Removes the cells containing graph related text.
        contents = cell_remover(contents, "GRAPH_TEXT")
        # removes graph lines from cell
        contents = line_remover(contents, "GRAPH_LINE")

    # Assigns file name based on excel data
    compressed_data_file_path = flight_data_file_path + compressed_data_file_name + ".pkl"
    # This replaces the file path to the compressed data
    contents = contents.replace("COMPRESSED_DATA_FILE_PATH", "\\\"" +
                                (compressed_data_file_path
                                 ).replace("\\", jupyter_sep) + "\\\"")

    # Checks to see if the start and end time are in the correct format
    hours_valid = []
    for flight in range(number_of_flights):
        try:
            int(start_times_hours[flight])
            hours_valid.append(True)
        except ValueError:
            hours_valid.append(False)
        try:
            int(end_times_hours[flight])
            hours_valid.append(True)
        except ValueError:
            hours_valid.append(False)
    # Checks to see if ICAO code is valid, if not then the Metar information is
    # removed
    metar_data_list = []
    metar_generated = []
    for flight in range(number_of_flights):
        if include_metar is True:
            flight_date = str(flight_dates[flight])
            if (icao_airfields[flight] != "data" or icao_airfields[flight] != "") and all(hours_valid) is True:
                # Retrieves METAR data.
                metar_data_list.append(metar_finder(icao_airfields[flight], str(flight_date[:4]),
                                                    str(flight_date[4:6]), str(flight_date[6:8]),
                                                    str(flight_date[4:6]), str(flight_date[6:8]),
                                                    str(start_times_hours[flight]), str(end_times_hours[flight]),
                                                    metar_file_path))
                metar_generated.append(True)
            else:
                metar_generated.append(False)

    # Generates a list of months and years from flight_dates to be used in the metar functions
    days = []
    months = []
    years = []
    for flight in range(number_of_flights):
        days.append(int(str(flight_dates[flight])[6:8]))
        months.append(int(str(flight_dates[flight])[4:6]))
        years.append(int(str(flight_dates[flight])[:4]))

    if all(metar_generated) is not False and include_metar is True:
        for metar_data in metar_data_list:
            # Checks to see if METAR data is available.
            if len(metar_data) != 0:
                # Checks to see if the quota limit has been reached.
                if metar_data[0] == "Quota limit reached.":
                    # If the limit has been reached then it puts in a line of code
                    # to re-try when the quota limit has been reached.
                    contents = metar_quota_returner(contents,
                                                    flight_log_file_name_header +
                                                    compressed_data_file_name +
                                                    ".ipynb", icao_airfields,
                                                    years,
                                                    months,
                                                    days,
                                                    months,
                                                    days,
                                                    start_times_hours,
                                                    end_times_hours,
                                                    metar_file_path, number_of_flights,
                                                    replace_key="METAR_" +
                                                                "INFORMATION")
                    # Replaces JFLTS METAR text with nothing if data is available.
                    contents = contents.replace("METAR_LINE", "")
                    contents = contents.replace("METAR_TEXT", "")
                else:
                    # Includes METAR data into the contents.
                    contents = metar_returner(metar_data, contents,
                                              months,
                                              years, number_of_flights,
                                              replace_key="METAR_INFORMATION")
                    # Replaces JFLTS METAR text with nothing if data is available.
                    contents = contents.replace("METAR_LINE", "")
                    contents = contents.replace("METAR_TEXT", "")
            else:
                contents = no_metar_returner(icao_airfields, flight_dates,
                                             flight_dates,
                                             start_times_hours, end_times_hours,
                                             contents, number_of_flights,
                                             replace_key="METAR_INFORMATION")
                # Replaces JFLTS METAR text with nothing if data is available
                contents = contents.replace("METAR_LINE", "")
                contents = contents.replace("METAR_TEXT", "")
    else:
        # Removes METAR related cells and lines.
        contents = cell_remover(contents, "METAR_INFORMATION")
        contents = line_remover(contents, "METAR_LINE")
        contents = cell_remover(contents, "METAR_TEXT")

    # Formats dictionary appropriately to be put into the jupyter notebook as text
    weather_information = ""
    runway_information = ""
    for flight in range(number_of_flights):
        weather_information += dictionary_reader(weather_data_lists[flight], debug_name="Weather data",
                                                 units_present=True, flight_index=flight,
                                                 flight_number=(str(flight_numbers[flight] + " " +
                                                                str(flight_dates[flight])))) + ","
        runway_information += dictionary_reader(runway_data_lists[flight], debug_name="Runway data",
                                                units_present=False, flight_index=flight,
                                                flight_number=(str(flight_numbers[flight] + " " +
                                                               str(flight_dates[flight])))) + ","
    weather_information = weather_information[:-1]  # Removes the last "," for json formatting
    runway_information = runway_information[:-1]  # Removes the last "," for json formatting

    if "empty_dictionary" not in weather_information:  # If information is present, add it to the content.
        contents = contents.replace("\"WEATHER_INFORMATION\"", "\"<h2>Weather Information</h2><a class=\\\"anchor\\\"" +
                                    " id=\\\"Weather-Information\\\"></a>\\n\"" + ",\n   \"\\n\",\n   " +
                                    weather_information)  # Creates a formatted title
        contents = contents.replace("WEATHER_LINE", "")
        contents = contents.replace("WEATHER_TEXT", "")
    else:
        # Removes Weather related cells and lines.
        contents = cell_remover(contents, "WEATHER_INFORMATION")
        contents = line_remover(contents, "WEATHER_LINE")
        contents = cell_remover(contents, "WEATHER_TEXT")
        contents = contents.replace("WEATHER_INFORMATION", "")

    if "empty_dictionary" not in runway_information:  # If information is present, add it to the content.
        contents = contents.replace("\"RUNWAY_INFORMATION\"", "\"<h2>Runway Information</h2><a class=\\\"anchor\\\"" +
                                    " id=\\\"Runway-Information\\\"></a>\\n\"" + ",\n   \"\\n\",\n   " +
                                    runway_information)  # Creates a formatted title
        contents = contents.replace("RUNWAY_LINE", "")
        contents = contents.replace("RUNWAY_TEXT", "")
    else:
        # Removes runway related cells and lines.
        contents = cell_remover(contents, "RUNWAY_INFORMATION")
        contents = line_remover(contents, "RUNWAY_LINE")
        contents = cell_remover(contents, "RUNWAY_TEXT")
        contents = contents.replace("RUNWAY_INFORMATION", "")

    # Creates a new flight log from the contents
    flight_log_creator(contents, flight_log_file_path, compressed_data_file_name, flight_log_file_name_header)
    print('Pickling data')
    # Compresses the flight data for faster loading
    compile_and_compress(flight_data_file_path, flight_data_file_names,
                         csv_flight_data_file_path,
                         csv_flight_data_names, compressed_data_file_path)
    print('Flight log maker finished')


def flight_data(file_path, file_name):
    """This imports the data excel using pandas"""
    # Excel file.
    file_path_with_name = file_path + file_name
    # # Extracts data from each sheet.
    frame = pd.read_excel(file_path_with_name, sheet_name=None, engine='openpyxl')
    frame_list = []
    for data in frame.keys():
        frame_list.append(frame[data])
    return frame_list


def flight_data_and_axis(new_frames):
    """Returns list of lists with the following structure:
    [[flight, [data source, [name, unit, data],[name, unit, data]]], [flight, [data source, [name, unit, data],
    [name, unit, data]]]]."""
    # TODO: try rewriting this code in a more legible way.
    # Creates an empty list for all the data.
    values_list = []
    # Finds the flight date and number from the data
    flight_identifier = new_frames[0].columns[0][-16:]
    # Checks through all the data frames
    for frame in new_frames:
        # Goes through all the columns
        data_lists = []
        data_lists.append(frame.columns[0].split("_")[-3])
        unit_present = True
        for column in frame.columns:
            # Converts values from data frame into a list.
            y = frame[column].tolist()
            # This code creates the y-axis label.
            # Creates a name
            name = ""
            unit = ""
            # b is used to place a capital letter for the first letter.
            b = 0
            # This checks the length of the columns to check if units need to
            # be included.
            if len(column.split("_")) == 5:
                # a is used to check if the underscore has been reached.
                a = 0
                # unit_present is used to indicate that there is a unit.
                unit_present = True
            else:
                if len(column.split("_")) == 4:
                    # This indicates that there are no units for that
                    # particular value.
                    unit_present = False
                    a = 0
                else:
                    a = 5 - len(column.split("_"))

            # This for loop creates the name and unit data.
            for letter in column:
                if b == 0:
                    # Adds an uppercase letter to the start of the name
                    name = letter.upper()
                    # Sets b to 1 to indicate that a capital letter has been
                    # inserted.
                    b = 1
                else:
                    if a <= 0:
                        # Replaces underscore with a space.
                        if letter != "_":
                            # Adds letters to build up name.
                            name = name + letter
                        else:
                            # Increment a
                            a += 1
                            # If the name has more than one word in it, use
                            # a space as a separator
                            if a <= 0:
                                name += " "
                    else:
                        # TODO: unit_present is only set when a is 0 but only accessed when a is > 0. This is a problem.
                        if letter != "_" and unit_present is True:
                            unit = unit + letter
                        elif unit_present is False:
                            unit = "no unit"
                            break
                        else:
                            break
            # Replaces per with the superscript notation.
            if "per" in unit:
                # splits unit into list about per.
                unit_split = unit.split("per")
                # Creates a blank list for counting the number of occurrences.
                # of a particular denominator.
                denominators = []
                # a is used to check if the value is a numerator or a
                # denominator.
                a = 0
                for count in range(1, len(unit_split)):
                    # Checks through denominator list
                    for item in denominators:
                        # Checks if there is already a denominator with that
                        # unit.
                        if unit_split[count] in item[0]:
                            # If there is then it increases the power of that
                            # unit.
                            item[1] = item[1] + 1
                            # Sets the check to 1 to show that this unit has
                            # appeared before.
                            a = 1
                    # Checks if the denominator has appeared before.
                    if a == 1:
                        a = 0
                    else:
                        # If not it creates a new entry.
                        denominators.append([unit_split[count], 1])
                # recreates unit.
                unit = unit_split[0]
                # Goes through each denominators and formats adds it to the
                # unit list.
                for denominator in denominators:
                    # Puts units in format with powers
                    unit = unit + denominator[0] + "$^{-" + \
                           str(denominator[1]) + "}$"
            data_lists.append([name, unit, y])
        values_list.append(data_lists)
    return [flight_identifier, values_list]


def flight_log_creator(contents, file_path, file_name_data,
                       file_name_header="Flight_Log_"):
    """This creates or overwrites a file with the name file_name_header date
     flight_numbers.ipynb  and fills the file with the
    contents provided as an input."""
    # Creates file with name
    print('Creating new flight log')
    file = open(file_path + os.sep + file_name_header + file_name_data + ".ipynb", "w+")
    # Extracts contents.
    file.write(contents)
    # Closes the file.
    file.close()


def flight_data_time_sorter(frame_list):
    """Splits the data by the title containing time."""
    a = 0
    # Creates a blank dictionary for the time columns.
    renamed_time_columns = {}
    # Empty list to be populated by columns that contain time.
    time_columns = []
    # Empty list for new frames to fill.
    new_frames = []
    # Edits one frame at a time.
    for frame_data in frame_list:
        # Empty list to be populated by columns that contain time more than
        # once.
        frame_columns_list = []
        # Columns is a list of columns.
        columns = frame_list[a].columns
        # Increments a
        a = a + 1
        # Loops through each column to see if it contains the word time.
        for column_data in columns:
            # Checks to see if the word time appears in the column.
            try:
                if "action_time" in column_data.lower():
                    # Exceptons are passed here.
                    pass
                elif "time" in column_data.lower():
                    # If time appears then it is appended to the list time_columns.
                    time_columns.append(column_data)
                    # Divides column by 1*10^6 to return it to seconds.
                    frame_data[column_data] = frame_data[column_data].div(10 ** 6)
                    # Adds columns in this data frame that contain the word time to
                    # a list.
                    frame_columns_list.append(column_data)
                    # appends replacement column to dictionary.
                    renamed_time_columns[column_data] = (column_data.replace("_US_", "_s_"))
            except TypeError:  # This exception is for the user collected environmental data time
                if "dummy_time" in column_data.lower():
                    frame_columns_list.append(column_data)
                else:
                    pass

        # Creates a copy of the columns to delete parts from.
        frame_copy = frame_data.copy()
        # The variable b will be used to divide the list.
        b = 0
        # This variable is used to trigger the appending of the data frames to
        # the list data frames.
        d = 0
        # Checks through each of the columns.
        frame_duplicate = None
        for column_data in columns:
            if b == 0:
                frame_duplicate = frame_copy.copy()
                b = 1
                # Checks to see if column is a time column.
                for time_column in time_columns:
                    if column_data == time_column:
                        d = 1
                # Removes frames
                frame_copy = frame_copy.drop(labels=column_data, axis=1)
                if d == 1:
                    # Removes columns from the frame_duplicate list
                    for column_drop in frame_copy.columns:
                        frame_duplicate = frame_duplicate.drop(labels=column_drop, axis=1)
                    # Checks if time appears in column being checked.
                    new_frames.append(frame_duplicate)
                    b = d = 0
            else:
                # Checks to see if column is a time column.
                for time_column in time_columns:
                    if column_data == time_column:
                        d = 1
                # Removes frames
                frame_copy = frame_copy.drop(labels=column_data, axis=1)
                if d == 1:
                    # Removes columns from the frame_duplicate list
                    for column_drop in frame_copy.columns:
                        frame_duplicate = frame_duplicate.drop(labels=column_drop, axis=1)
                    # Checks if time appears in column being checked.
                    new_frames.append(frame_duplicate)
                    b = d = 0
    # Creates a blank list for the frames with the seconds unit fixed.
    arranged_frames = []
    # Renames columns and changes the units of time from US (microseconds) to s
    for frame_data in new_frames:
        # Replaces the unit
        frame_data.rename(columns=renamed_time_columns, inplace=True)
        # Appends the frame.
        arranged_frames.append(frame_data)
    return arranged_frames


def file_type_finder(file_path, extension):
    """ Returns files of a particular type given an input file path
    and extension."""
    # Finds list of files in file_path.
    files = os.listdir(file_path)
    # Reversed extension
    reversed_extension = extension[::-1]
    # removes the . from the file extension.
    reversed_extension = reversed_extension[:-1]
    # Creates empty list of files to check.
    required_files = []
    # Looks through each file individually.
    for file in files:
        # Empties rev_file_extension.
        rev_file_extension = ""
        # a is used to indicate that the . before the file extension has been
        # reached, it is set to 0 to reset it.
        a = 0
        for character in reversed(file):
            # Adds characters from file name to rev_file_extension if the dot
            # has not been reached yet.
            if character != "." and a == 0:
                # Adds letters to filenames.
                rev_file_extension = rev_file_extension + character
            else:
                a = 1
        # If the . has been reached and the file extension matches the
        # requested extension then the file name is added to a list of suitable
        # files.
        if a == 1 and rev_file_extension == reversed_extension:
            required_files.append(file)
    return required_files


def date_and_flight_number(frames):
    """This function finds the date and flight number from the headings in
    the list of frames provided by the function flight data"""
    # Starts at the data frame (first sheet).
    for frame_date in frames:
        # Scans through the columns.
        for column_date in frame_date.columns:
            # Splits column name by the underscore.
            lines = column_date.split("_")
            # Finds length of columns.
            a = len(lines)
            # If columns are too short to have name, unit, date and Flight
            # Number then it tries the next column.
            if a >= 3:
                # Checks the penultimate value.
                date = lines[a - 2]
                # Removes the word flight from the final value to leave just
                # the Flight Number
                flight_number = lines[a - 1][6:]
                # Returns the Date and the Flight Number
                return date, flight_number


def csv_frame(flight_data_file_path, csv_flight_data_name):
    """Takes file path of csv flight data and returns a pandas data frame_micro."""
    # Creates file path from graph file path and file name
    file_path = flight_data_file_path + os.sep + csv_flight_data_name
    if csv_flight_data_name == "" or flight_data_file_path == "":
        return pd.DataFrame()
    # Reads CSV
    frame_micro = pd.read_csv(file_path)
    return frame_micro


def compile_and_compress(flight_data_file_path, flight_data_file_name,
                         csv_data_file_path, csv_data_file_name,
                         comp_data_file_path):
    """
    This is used to compile all the entered data. This is then pickled and saved for faster loading.

    flight_data_file_names and csv_data_file_name are of type list.
    """
    values_list = []
    for data_set in range(len(flight_data_file_name)):
        # Excel Sheets
        print(flight_data_file_name[data_set])
        frame_list = flight_data(flight_data_file_path, flight_data_file_name[data_set])
        # Retrieves csv flight data if present
        if csv_data_file_name != ['']:
            csv_flight_data_frame = csv_frame(csv_data_file_path,
                                              csv_data_file_name[data_set])
            # Appends csv frame to flight data from pixhawk
            frame_list.append(csv_flight_data_frame)
        # Sorts frames by time
        sorted_frames = flight_data_time_sorter(frame_list)
        values = flight_data_and_axis(sorted_frames)
        # Creates a list of all the values.
        values_list.append(values)
    # Compresses (pickles) the data and saves it in the excel files folder.
    pk.dump(values_list, open(comp_data_file_path, "wb"))
    print('Pickling finished')


def dictionary_reader(dictionary, debug_name="Dictionary data", units_present=False, flight_index=0,
                      flight_number=""):
    """Takes a dictionary of data and outputs a formatted string in the form of a table"""
    # Splits the dictionary into lists of values and keys
    dictionary_keys = list(dictionary.keys())
    dictionary_values = list(dictionary.values())
    if dictionary == {'': 'N/A'}:
        text = "\"empty_dictionary \\n\""
    else:

        try:
            text = ""

            units = []
            names = []
            if units_present is True:
                # Removes the _ from the names and separates the units from the variable names
                for key in dictionary_keys:
                    units.append(str(key).split("_")[-1])
                    names.append(str(key).split("_")[:-1])
            else:
                # Removes the _ from the names
                for key in dictionary_keys:
                    names.append(str(key).split("_"))

            # Joins up variable names in case they are two words
            joined_names = []
            for name_array in names:
                name = ""
                for part in name_array:
                    name += part + " "
                joined_names.append(name)

            if units_present is True:
                joined_names, units, dictionary_values = zip(*sorted(zip(
                    joined_names, units, dictionary_values)))  # Sort alphabetically
            else:
                joined_names, dictionary_values = zip(*sorted(zip(
                    joined_names, dictionary_values)))  # Sort alphabetically

            if flight_index == 0:
                # Create a header for the table
                header = "\"\\n\", \" | Flight |"
                if units_present is True:
                    for data_item in range(len(dictionary_keys)):
                        header += " " + str(joined_names[data_item]) + " (" + str(units[data_item]) + ") |"
                else:
                    for data_item in range(len(dictionary_keys)):
                        header += " " + str(joined_names[data_item]) + " |"
                text = header + "\", \n "
                # Creates the next empty row
                counter = 0
                text += "\"\\n\", \" | --- |"
                while counter <= len(dictionary_keys) - 1:
                    text += " --- |"
                    counter += 1
                text += "\", \n   "
            else:
                text = ""

            # Adds data to the table
            text += "\"\\n |" + " Flight " + str(flight_number) + "|"
            for data_item in range(len(dictionary_keys)):
                text += " " + str(dictionary_values[data_item]) + " |"

            text += "\"  \n   "

        except ValueError:
            print("{0} not entered or in an incorrect format in the Input_File.json. ".format(debug_name) +
                  "Format should be \"variable_unit\": \"value\"")
            text = ""

    return text


def multi_dictionary_data_formatter(dictionaries, flight_dates, debug_name):
    """Takes in a dictionaries of data with possibly multiple data sets separated by a "," and
    formats them into lists of dictionaries which each contain one data set.

    flight_dates is used to determine the number of flights

    e.g.: dictionaries{key} = {value_dataset_1, value__dataset_2}
    into:
    [{key}=value_dataset_1, {key}=value_dataset_2]

    returns a list of dictionaries
    """

    dictionary = []
    if len(dictionaries.keys()) == 0:
        # If the lists are empty, create blank templates
        for time in range(len(flight_dates)):
            dictionary.append({"": "N/A"})
    else:
        # Removes any blank fields in the dictionaries:
        for key in dictionaries.keys():
            if dictionaries[key] == "":
                dictionaries = remove_dictionary_key(dictionaries, key)
            else:
                pass

        # Checks that the dictionary data lengths are equal to the number of flights
        for item in dictionaries.values():
            if len(item.replace(" ", "").split(",")) == len(flight_dates):
                pass
            else:
                raise IndexError("{} data content does not match the number"
                                 " of flights entered ({}).".format(debug_name, len(flight_dates)))

        # Formats dictionaries data as lists of data dictionaries
        for flight in range(len(flight_dates)):
            # Creates a new dictionary for each set of data
            dictionary_data_temp = {}
            for key in dictionaries.keys():
                dictionary_data_temp[key] = dictionaries[key].replace(" ", "").split(",")[flight]
            dictionary.append(dictionary_data_temp)

    return dictionary


def remove_dictionary_key(dictionary, key):
    """Used to delete a key in a dictionary"""
    new_dictionary = dict(dictionary)
    del new_dictionary[key]
    return new_dictionary


def multi_string_data_formatter(data_string, flight_dates, debug_name):
    """Takes a string of multiple inputs separated by a "," and separates this into a list of multiple inputs.

    flight_dates a list used to verify that enough data has been entered (is equal to len(flight_data)).

    e.g. data_string = "1234,4567"
    output = [1234, 4567]
    """

    data_list = str(data_string).replace(" ", "").split(",")
    if len(data_list) != len(flight_dates) and data_list != [""]:
        raise IndexError("{} data entered does not have the same length as the number of flights ({})"
                         .format(debug_name, len(flight_dates)))

    return data_list
