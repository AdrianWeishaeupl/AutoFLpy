
import pandas as pd
import pickle as pk
import os
from openpyxl import load_workbook
from autoflpy.util.metar_processing import *
from autoflpy.util.text_manipulation import *


"""
Flight Log Generation Code.
This code takes flight data in the form of an .xlsx document (generated from a
.log file in log_to_xlsx.py) and plots and
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
                     flight_data_file_names, arduino_flight_data_file_path,
                     arduino_flight_data_names, flight_dates, flight_numbers,
                     flight_log_file_name_header, checklist_file_path,
                     icao_airfields, start_times_hours, end_times_hours, metar_file_path,
                     weather_data_lists, runway_data_lists):
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
    # Checks to see whether there is graph data or arduino data that can be
    # used to plot graphs by checking if the path exists and if the path has a
    # suitable length to that it is not just greater than 1.
    directories_present = []
    for flight in range(number_of_flights):
        if (os.path.exists(flight_data_file_path + os.sep + flight_data_file_names[flight])
            is True and
            len(flight_data_file_path + os.sep + flight_data_file_names[flight]) > 1) \
            or \
            (os.path.exists(arduino_flight_data_file_path + os.sep +
                            arduino_flight_data_names[flight]) is True and
             len(arduino_flight_data_file_path + os.sep +
                 arduino_flight_data_names[flight]) > 1):
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

    def remove_checklist_line_from_template(contents_checklist_rm):
        contents_checklist_rm = line_remover(contents_checklist_rm, "CHECKLIST_LINE")
        contents_checklist_rm = cell_remover(contents_checklist_rm, "CHECKLIST_INFORMATION")
        return contents_checklist_rm

    # Creates a list of all nominal frames from the nominal checklist.
    if checklist_file_path != "data" or checklist_file_path != "":
        try:
            frame_list_nominal = flight_data(checklist_file_path,
                                             "Checklists_nominal.xlsx")
            frame_list_emergency = flight_data(checklist_file_path,
                                               "Checklists_emergency.xlsx")
            print('Looking for checklists')
            filtered_frame_nominal_concat = []  # For combining checklist data frames into one
            filtered_frame_emergency_concat = []  # For combining checklist data frames into one
            for flight in range(number_of_flights):
                filtered_frame_nominal_concat.append(checklist_finder(frame_list_nominal,
                                                                      flight_numbers[flight],
                                                                      flight_dates[flight]))

                # Filters the data to get just the required data.
                filtered_frame_emergency_concat.append(checklist_finder(frame_list_emergency,
                                                                        flight_numbers[flight],
                                                                        flight_dates[flight]))
            # Combining checklist data frames into one:
            filtered_frame_nominal = pd.concat(filtered_frame_nominal_concat)
            filtered_frame_emergency = pd.concat(filtered_frame_emergency_concat)
            contents = flight_log_checklist(filtered_frame_nominal,
                                            filtered_frame_emergency,
                                            "CHECKLIST_INFORMATION",
                                            contents)[0]
            # Removes checklist related lines if no checklist data available
            # and removes checklist line labels if checklist can be used.
            if flight_log_checklist(filtered_frame_nominal,
                                    filtered_frame_emergency,
                                    "CHECKLIST_INFORMATION",
                                    contents)[1] is False:
                contents = remove_checklist_line_from_template(contents)
            else:
                contents = contents.replace("CHECKLIST_LINE", "")
        except ValueError:
            contents = remove_checklist_line_from_template(contents)
            print("Checklist not found")
        except PermissionError:
            contents = remove_checklist_line_from_template(contents)
            print("Unable to open the checklist, check that it is not open "
                  "else where")
        except UnboundLocalError:
            contents = remove_checklist_line_from_template(contents)
            print("Check checklists contain all of the relevant information")
        except FileNotFoundError:
            contents = remove_checklist_line_from_template(contents)
            print("Checklist not found, check that the checklist exists and is\
                  in the correct location")
    else:
        contents = remove_checklist_line_from_template(contents)
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
        flight_date = str(flight_dates[flight])
        if (icao_airfields[flight] != "data" or icao_airfields[flight] != "") and all(hours_valid) is True:
            # Retrieves METAR data.
            metar_data_list.append(metar_finder(icao_airfields[flight], flight_date[:4],
                                                flight_date[4:6], flight_date[6:8],
                                                flight_date[4:6], flight_date[6:8],
                                                start_times_hours[flight], end_times_hours[flight],
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

    if all(metar_generated) is not False:
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
                                                 units_present=True) + ","
        runway_information += dictionary_reader(runway_data_lists[flight], debug_name="Runway data",
                                                units_present=False) + ","
    weather_information = weather_information[:-1]  # Removes the last "," for json formatting
    runway_information = runway_information[:-1]  # Removes the last "," for json formatting

    if weather_information != "\"\\n\"":  # If information is present, add it to the content.
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

    if runway_information != "\"\\n\"":  # If information is present, add it to the content.
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
                         arduino_flight_data_file_path,
                         arduino_flight_data_names, compressed_data_file_path)
    print('Flight log maker finished')


def flight_data(file_path, file_name):
    """This imports the data excel using pandas"""
    # Excel file.
    file_path_with_name = file_path + file_name
    data = load_workbook(file_path_with_name, read_only=True)
    sheet_list = data.sheetnames
    # Creates empty list for frames.
    frame_list = []
    # Extracts data from each sheet.
    for sheet in sheet_list:
        frame = pd.read_excel(data, sheet_name=sheet, engine='openpyxl')
        frame_list.append(frame)
    return frame_list


def checklist_finder(frame_list, flight_number, date):
    """This automatically returns the relevant information for a given flight
    number."""
    b = 0
    # goes through each frame
    for frame in frame_list:
        # Checks through each column in each frames
        for column in frame.columns:
            # If a column contains the word Checklist and the word checklist
            # has not previously appeared then b is set to 1 to stop the loops
            # and record the frame.
            if "Checklist" in column:
                b = 1
                break
        if b != 0:
            break
    # The required frame is then recorded.
    checklist_frame = frame
    # Then after scanning through the frames, the correct flight numbers are
    # found.
    for column in checklist_frame.columns:
        # Then it searches for the flight number column.
        if "flight number" in column.lower():
            flight_number_column = column
            # Once found it breaks out of the for loop.
            break
    # Filters Frame by flight number, removing any rows that do not match
    flight_number = float(flight_number)
    flight_number_filtered = \
        checklist_frame[checklist_frame[flight_number_column] == flight_number]
    # Converts index to list
    index = flight_number_filtered.index.values.tolist()
    # Creates a list with times
    times = flight_number_filtered[flight_number_filtered.columns[2]].tolist()
    # Creates an empty list of rows to be removed
    rows = []
    # For the items in index, the time is converted to the same format as the
    # date and if they are not equal, then that index is added to rows to be
    # removed.
    for a in range(len(index)):
        if str(times[a]).split(" ")[0].replace("-", "") == str(date):
            rows.append(index[a])
    # Removes row if its index equals a row to be removed.
    filtered_frame = flight_number_filtered[
        flight_number_filtered.index.isin(rows)]
    return filtered_frame


def flight_log_checklist(filtered_frame_nominal, filtered_frame_emergency,
                         replace_key, contents):
    """This automatically edits the Jupyter notebook file to include the
    checklist data in the flight test log in Jupyter, the name of the notebook
    is required along with the the file path of Notebook (Notebook_file_path),
    the replace key is a string which consists of capital letters that will be
    alone in a markdown cell in the document, this cell will be replaced by the
    checklist information gathered by the code. The checklist file path is
    required which is where the checklists are situated."""
    # Separates lines out.
    filtered_nominal = filtered_frame_nominal
    # Nominal_Checklist
    checklists_actioned = filtered_nominal["Nominal Checklist"].tolist()  # Checklist type e.g. Launch
    checklist_actioned_by = filtered_nominal["Name"].tolist()  # Filled in by this person

    start_date_time = filtered_nominal["Start time"].tolist()
    end_date_time = filtered_nominal["End time"].tolist()
    damage = filtered_nominal["Damage"].tolist()
    battery = filtered_nominal["Battery Voltages"].tolist()
    notes = filtered_nominal["Notes"].tolist()
    version_completed = None  # The version number of the nominal checklist
    for column in filtered_nominal.columns:
        # Iterate over all columns, find the checklist version column and then set version_completed
        if "Checklist (VER" in column:
            version_completed = filtered_nominal[column].tolist()
            break

    if version_completed is not None:
        version_completed.append("")  # Adds a default version value for no entered version values.
        version_completed = [val for val in version_completed if type(val) is str][0]

    # Emergency Checklist
    filtered_emergency = filtered_frame_emergency
    emergency_checklists_actioned = \
        filtered_emergency["Emergency Checklist"].tolist()  # Which checklist was actioned e.g. Motor Failure
    emergency_checklist_actioned_by = \
        filtered_emergency["Name"].tolist()  # Who actioned the checklist (name)
    emergency_start_date_time = filtered_emergency["Start time"].tolist()
    emergency_end_date_time = filtered_emergency["End time"].tolist()
    emergency_notes = filtered_emergency["Notes"].tolist()

    version_completed_emergency = None
    for column in filtered_emergency.columns:
        # Iterate over all columns, find the checklist version column and then set version completed
        if "Checklist (VER" in column:
            version_completed_emergency = filtered_emergency[column].tolist()
            break

    if version_completed_emergency is not None:
        version_completed_emergency.append("")  # Adds a default version value for no entered version values.
        version_completed_emergency = [val for val in version_completed_emergency if type(val) is str][0]

    # This is a list that will have all the data appended to it for the nominal
    # checklists in the next section.
    checklist_actioned_text = ""
    # This is a list that will have all the data appended to it for the
    # emergency checklists in the section after the next section.
    emergency_checklist_actioned_text = ""
    # This section returns who actioned which checklists and at what times,
    # as well as stating the notes that were recorded at the time and any
    # damage that may have occurred to the UAV.
    # This checks if there have been checklists actioned.
    if len(checklists_actioned) != 0:
        # Goes through each of the checklists and creates a list of all the
        # checklists actioned, who actioned them, when they were actioned and
        # the notes or damage that was recorded with them.
        for index in range(len(checklists_actioned)):
            text = "\n    \"The " + checklists_actioned[index] + \
                   " was actioned by " + checklist_actioned_by[index] + \
                   " starting at " + str(start_date_time[index]) + " and " + \
                   "ending at " + str(end_date_time[index]) + "."
            # If there are notes, then append them to the text with the
            # following text.
            if str(notes[index]) != "nan":
                text += " The notes recorded on this checklist were: " + \
                        "<i>" + notes[index]
            # Adds full stop to end if required.
            if text[-1:] != "." and text[-1:] != "!" and text[-1:] != "?":
                text += "."
            text += "</i>"
            # If there is damage recorded, then append them to the text with
            # the following text.
            if str(damage[index]) != "nan":
                text = text + " Damage was reported on this flight as:" + \
                       " <i>" + damage[index]
                # Adds full stop to end if required.
                if text[-1:] != "." and text[-1:] != "!" and text[-1:] != "?":
                    text += "."
                text += "</i>"
            if str(battery[index]) != "nan":
                text = text + " The battery voltages of each battery are: <i>" + str(battery[index])
                # Adds full stop to end if required.
                if text[-1:] != "." and text[-1:] != "!" and text[-1:] != "?":
                    text += "."
                text += "</i>"
            text = text + "\\n\",\n    \"\\n\","
            # This adds the text to the current string
            checklist_actioned_text += text
    # This code does the same as the previous section but for the emergency
    # checklists.
    # This section returns who actioned which checklists and at what times,
    # as well as stating the notes that were recorded at the time and any]
    # damage that may have occurred to the UAV.
    # This checks if there have been checklists actioned.
    if len(emergency_checklists_actioned) != 0:
        # Goes through each of the emergency checklists and creates a list of
        # all the emergency checklists actioned, who actioned them, when they
        # were actioned and the notes that were recorded with them.
        for index in range(len(emergency_checklists_actioned)):
            text = "\n    \"The " + emergency_checklists_actioned[index] + \
                   " was actioned by " + \
                   emergency_checklist_actioned_by[index] + \
                   " starting at " + str(emergency_start_date_time[index]) + \
                   " and ending at " + str(emergency_end_date_time[index]) + "."
            # If there are notes, then append them to the text with the
            # following text.
            if str(emergency_notes[index]) != "nan":
                text += " The notes recorded on this checklist were: " + \
                        "<i>" + emergency_notes[index]
            # Adds full stop to end if required.
            if text[-1:] != "." and text[-1:] != "!" and text[-1:] != "?":
                text += "."
            text += "</i>"
            text = text + "\\n\",\n    \"\\n\","
            # This adds the text to the current string
            emergency_checklist_actioned_text += text
    # checklist_list is the list of checklists with a string to go ahead of
    # the word checklist in the text in Jupyter. For example, some data which
    # will be appended to this list later is: [emergency_checklists_actioned,
    # " emergency"].
    checklist_list = []
    if len(checklists_actioned) != 0:
        checklist_list.append([checklists_actioned, ""])
        nom = 1
    else:
        nom = 0
    if len(emergency_checklists_actioned) != 0:
        checklist_list.append([emergency_checklists_actioned, " emergency"])
        eme = 1
    else:
        eme = 0
    flight_duration_columns = []
    # This creates a list to contain the recorded flight duration and who
    # actioned them
    flight_duration_data = []
    # Goes through nominal dataframe and finds all columns that contain the
    # the word Flight Duration
    for column in filtered_frame_nominal.columns:
        if "Flight Duration" in column:
            flight_duration_columns.append(
                filtered_frame_nominal[column].tolist())
    # This finds the contents of the columns and who made them and appends that
    # data to the list flight_duration_data
    for column in flight_duration_columns:
        for index in range(len(column)):
            if str(column[index]) != "nan" and str(column[index]).lower != "Null":
                flight_duration_data.append([checklist_actioned_by[index],
                                             column[index]])
    # This clears the flight duration column list so the emergency data can be
    # checked.
    flight_duration_columns = []
    # Goes through nominal dataframe and finds all columns that contain the
    # the word Flight Duration
    for column in filtered_frame_emergency.columns:
        if "Flight Duration" in range(len(column)):
            flight_duration_columns.append(
                filtered_frame_emergency[column].tolist())
    # This clears the flight duration column list so the emergency data can be
    # checked.
    flight_duration_columns = []
    # This finds the contents of the columns and who made them and appends that
    # data to the list flight_duration_data
    for column in flight_duration_columns:
        for index in column:
            if str(column[index]) != "nan" and str(column[index]).lower != "Null":
                flight_duration_data.append(
                    [emergency_checklist_actioned_by[index],
                     column[index]])
    if len(flight_duration_data) == 0:
        # fdi stands for Flight Duration Info and it is there to show if the
        # Flight Duration was recorded.
        fdi = 0
    else:
        fdi = 1
    text_list = []
    # uses data to find which checklists have been run.
    for checklist_item in checklist_list:
        # Creates a blank list to be filled with the
        # Checklists actioned and the number of times that checklist had been
        # actioned.
        checklist_and_number = []
        # b is used to append the first item to the list checklist_and_number
        b = 0
        # This goes through all the checklists and counts how many times that
        # they appear.
        for checklist in checklist_item[0]:
            if b == 1:
                # a is used to indicate that that checklist of that type has
                # appeared before.
                a = 0
                for index in range(len(checklist_and_number)):
                    if checklist_and_number[index][0] == checklist:
                        checklist_and_number[index][1] += 1
                        a = 1
                        break
                if a == 0:
                    checklist_and_number.append([checklist, 1])
            else:
                checklist_and_number.append([checklist, 1])
                b = 1
        # Checks if the checklist contains more than one item
        if len(checklist_and_number) > 1:
            # Checks if the checklist has more than 2 items
            if len(checklist_and_number) >= 2:
                # Starts the string
                text = "The "
                # Creates a blank list for all the checklists repeated more
                # than once.
                number_greater_than_1 = []
                # loops through all the checklists actioned and adds lines of
                # text where required
                for checklist in checklist_and_number[:-1]:
                    text = text + checklist[0] + ", "
                    # If the checklist appears more than once then it is
                    # appended to the list along with the number of times it
                    # appears.
                    if checklist[1] > 1:
                        number_greater_than_1.append(checklist)
                    # This removes the Oxford comma.
                text = text[:-2] + " "
                # This does the last item in the list of checklists
                text = text + "and " + checklist_and_number[-1:][0][0] + \
                       checklist_item[1] + " checklists were actioned"
                # This checks the last item in the list checklist_and_number to
                # see if it should appear in the list with items that appear
                # more than once.
                if checklist_and_number[-1:][0][1] > 1:
                    short_1 = checklist_and_number[-1:][0][0]
                    short_2 = checklist_and_number[-1:][0][1]
                    number_greater_than_1.append([short_1, short_2])
                # Checks to see if the list has length 1.
                if len(number_greater_than_1) == 1:
                    text = text + " and " + number_greater_than_1[0][0] + \
                           " was actioned " + str(number_greater_than_1[0][1]) \
                           + " times."
                # if it does not then it loops through the lists.
                else:
                    if len(number_greater_than_1) != 0:
                        text = text + " and "
                        for repeat in number_greater_than_1[:-1]:
                            text = text + repeat[0] + " was actioned " + \
                                   str(repeat[1]) + " times, "
                            # This removes the Oxford comma.
                        text = text[:-2] + " "
                        text = text + "and " + number_greater_than_1[-1:][0][0] + " was actioned " + \
                               str(number_greater_than_1[-1:][0][1]) + " times."
                    else:
                        text = text + "."
        # This else is for it it only has one item
        else:
            # Checks if that checklist is repeated multiple times and then it
            # will state how many times it was repeated.
            if checklist_and_number[0][1] == 1:
                text = "The " + checklist_and_number[0][0] + checklist_item[1] \
                       + " checklist was actioned."
            else:
                text = "The " + checklist_and_number[0][0] + checklist_item[1] \
                       + " checklist was actioned " + \
                       str(checklist_and_number[0][1]) + " times."
        text_list.append(text)
    # Checks to see if the emergency checklist is available and replaces it
    # with a blank space if it is not
    if fdi == 1:
        flight_duration_text = ""
        for data in flight_duration_data:
            # TODO: Give a link to the checklist document?
            flight_duration_text = flight_duration_text + "\n    \"The " + \
                                   "flight Duration was recorded as: " + \
                                   str(data[1]) + ", this data was recorded by " + \
                                   str(data[0]) + ".\\n\",\n    \"\\n\","
    else:
        flight_duration_text = ""
    if eme == 0:
        text_list.append("")
    # Checks to see if the nominal checklist is available and replaces it with
    # a blank space if it is not.
    if nom == 0:
        text_list.insert(0, "")
    # If nominal checklists were used then show the version number.
    if nom == 1:
        version_completed_text = "\n    \"The checklist " + \
                                 "version used was " + version_completed + ".\\n\""
    else:
        version_completed_text = ""
    # If emergency checklists were used then show the version number.
    if eme == 1:
        version_completed_emergency_text = "\n    \"The emergency " + \
                                           "checklist version used was " + version_completed_emergency + ".\""
        # if nominal checklist are to be displayed, add a comma to the end
        if nom == 1:
            version_completed_text = version_completed_text + ","
    else:
        version_completed_emergency_text = ""
    checklist_replacement = "\n  {\n " + \
                            "  \"cell_type\": \"markdown\",\n" + \
                            "   \"metadata\": {},\n" + \
                            "   \"source\": [\n" + \
                            "    \"" + replace_key + "\"\n" + \
                            "   ]\n" + \
                            "  },"
    checklist_information = "  {\n " + \
                            "  \"cell_type\": \"markdown\",\n" + \
                            "   \"metadata\": {},\n" + \
                            "   \"source\": [\n" + \
                            "    \"<h2>Checklist Information</h2><a class=\\\"anchor\\\" " + \
                            "id=\\\"Checklist-Information\\\"></a>\\n\",\n    \"\\n\",\n" + \
                            "    \"" + text_list[0] + " " + text_list[1] + "\\n\",\n    " + \
                            "\"\\n\"," + flight_duration_text + checklist_actioned_text + \
                            emergency_checklist_actioned_text + version_completed_text + \
                            version_completed_emergency_text + \
                            "\n   ]\n" + \
                            "  },"
    # Checks to see if there is any relevant checklists and removes them if
    # there is not.
    checklist_exist = True
    if filtered_frame_nominal.shape[0] == 0 and filtered_frame_emergency.shape[0] == 0:
        checklist_information = ""
        checklist_exist = False
    contents = contents.replace(checklist_replacement, checklist_information)
    return contents, checklist_exist


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
                if "time" in column_data.lower():
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
                pass
        # Creates a copy of the columns to delete parts from.
        frame_copy = frame_data.copy()
        # The variable b will be used to divide the list.
        b = 0
        # This variable is used to trigger the appending of the data frames to
        # the list data frames.
        d = 0
        # Checks through each of the columns.
        # TODO: KEEP AN EYE ON THIS:
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


def arduino_micro_frame(flight_data_file_path, arduino_flight_data_name):
    """Takes file path of arduino micro flight data and returns a pandas data frame_micro."""
    # Creates file path from graph file path and file name
    file_path = flight_data_file_path + os.sep + arduino_flight_data_name
    if arduino_flight_data_name == "" or flight_data_file_path == "":
        return pd.DataFrame()
    # Reads CSV
    frame_micro = pd.read_csv(file_path)
    return frame_micro


def compile_and_compress(flight_data_file_path, flight_data_file_name,
                         arduino_data_file_path, arduino_data_file_name,
                         comp_data_file_path):
    """
    This is used to compile all the entered data. This is then pickled and saved for faster loading.

    flight_data_file_names and arduino_data_file_name are of type list.
    """
    values_list = []
    for data_set in range(len(flight_data_file_name)):
        # Excel Sheets
        print(flight_data_file_name[data_set])
        frame_list = flight_data(flight_data_file_path, flight_data_file_name[data_set])
        # Retrieves arduino flight data if present
        if arduino_data_file_name != ['']:
            arduino_flight_data_frame = arduino_micro_frame(arduino_data_file_path,
                                                            arduino_data_file_name[data_set])
            # Appends arduino frame to flight data from pixhawk
            frame_list.append(arduino_flight_data_frame)
        # Sorts frames by time
        sorted_frames = flight_data_time_sorter(frame_list)
        values = flight_data_and_axis(sorted_frames)
        # Creates a list of all the values.
        values_list.append(values)
    # Compresses (pickles) the data and saves it in the excel files folder.
    pk.dump(values_list, open(comp_data_file_path, "wb"))
    print('Pickling finished')


def dictionary_reader(dictionary, debug_name="Dictionary data", units_present=False):
    """Takes a dictionary of data and outputs a formatted string"""
    # Splits the dictionary into lists of values and keys
    dictionary_keys = list(dictionary.keys())
    dictionary_values = list(dictionary.values())
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

        # Adds any non empty values to the text string
        for data_item in range(len(dictionary_keys)):
            if dictionary_values[data_item] != "":
                if units_present is True:
                    text += "\"" + str(joined_names[data_item]) + \
                            ": " + str(dictionary_values[data_item]) + " " + str(units[data_item]) \
                            + "\\n\",  \"\\n\", \n   "
                else:
                    text += "\"" + str(joined_names[data_item]) + \
                            ": " + str(dictionary_values[data_item]) \
                            + "\\n\",  \"\\n\", \n   "
        text += "\"\\n\""

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

    returns dictionary
    """

    dictionary = []
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
