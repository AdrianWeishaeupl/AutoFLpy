import pandas as pd
import os
import textwrap
import matplotlib.pyplot as plt
from requests import get


"""
Flight Log Generation Code.
This code creates a GUI and should be launched from the "Automatic Flight Log
Maker.ipynb file (opened through Jupyter Notebook). It takes flight data in
the form of an .xls document (generated from a .log file in a previous step
in the same Jupyter Notebook) and plots and formats the data to be displayed
using a template .ipynb file.

@author Adrian Weishaeupl
aw6g15@soton.ac.uk 2019

based on work done by Samuel Pearson (sp1g18@soton.ac.uk) (06-08/2019)

"""

# Tries to import Metar, if it fails, it imports PIP and installs Metar
try:
    from metar import Metar
except ModuleNotFoundError:
    import pip._internal
    pip._internal.main(["install", "metar"])
    print("Installing METAR module")
except ImportError:
    import pip._internal
    pip._internal.main(["install", "metar"])
    print("Installing METAR module")


# Checsk to see if os.sep is \\
if os.sep == "\\":
    # If it is then it sets the jupyter sep to be \\\\\\\\ eight slashes so \\
    jupyter_sep = "\\\\\\\\"
else:
    jupyter_sep = "/"


def flight_log_maker(template_file_path, template_file_name,
                     flight_log_file_path, flight_data_file_path,
                     flight_data_file_name, arduino_flight_data_file_path,
                     arduino_flight_data_name, flight_date, flight_number,
                     flight_log_file_name_header, checklist_file_path,
                     log_code_version, ICAO_airfield,
                     start_time_hours, end_time_hours, metar_file_path):
    """This code will edit a specified template and return the result that has
    been produced after the substitution of data into the template."""
    print('Starting Flight Log Maker')
    flight_data_file_path_slash = flight_data_file_path.replace("\\",
                                                                jupyter_sep)
    arduino_flight_data_file_path_slash =\
        arduino_flight_data_file_path.replace("\\", jupyter_sep)
    # loads contents.
    contents = contents_opener(template_file_path, template_file_name)
    # Replaces the key for the flight log code version with the text
    contents = contents.replace("FLIGHT_LOG_CODE_VERSION",
                                log_code_version)
    # Inserts the date into the contents.
    contents = contents.replace("FLIGHT_DATE", str(flight_date))
    # Inserts the flight number into the contents.
    contents = contents.replace("FLIGHT_NUMBER", str(flight_number))
    # Checks to see wether there is graph data or arduino data that can be
    # used to plot graphs by checking if the path exists and if the path has a
    # suitable length to that it is not just greater than 1.
    if (os.path.exists(flight_data_file_path + os.sep + flight_data_file_name)
        is True and
        len(flight_data_file_path + os.sep + flight_data_file_name) > 1) \
        or\
        (os.path.exists(arduino_flight_data_file_path + os.sep +
                        arduino_flight_data_name) is True and
         len(arduino_flight_data_file_path + os.sep +
         arduino_flight_data_name) > 1):
        print('Importing xls data')
        # This replaces the file path with the neccissary information
        contents = contents.replace("PYTHON_FILE_PATH", "\\\"" +
                                    os.getcwd().replace("\\", jupyter_sep) +
                                    "\\\"")
        # This replaces the file path with the neccissary information
        contents = contents.replace("FLIGHT_DATA_FILE_PATH", "\\\"" +
                                    flight_data_file_path_slash + "\\\"")
        # Inserts the flight data file name into the contents.
        contents = contents.replace("FLIGHT_DATA_FILE_NAME",
                                    "\\\"" + flight_data_file_name + "\\\"")
        # Inserts the flight data file name into the contents.
        contents = contents.replace("ARDUINO_DATA_FILE_PATH", "\\\"" +
                                    arduino_flight_data_file_path_slash
                                    + "\\\"")
        # Inserts the flight data file path into the contents.
        contents = contents.replace("ARDUINO_DATA_FILE_NAME",
                                    "\\\"" + arduino_flight_data_name + "\\\"")
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
        # This is the text from the template that needs to be removed.
        flight_data_text = "flight_data_file_path = FLIGHT_DATA_FILE_PATH"
        # Removes the flight data file path into the contents.
        contents = contents.replace(flight_data_text, "")
        # This is the text from the template that needs to be removed.
        flight_data_text = "flight_data_file_name = FLIGHT_DATA_FILE_NAME"
        # Removes the flight data file path into the contents.
        contents = contents.replace(flight_data_text, "")
        # Removes the cell importing the graph data.
        contents = cell_remover(contents, "# GRAPH_DATA_IMPORT")
        # Removes the cells containg graph data.
        contents = cell_remover(contents, "\"MULTIAXIS_GRAPH\\n\"")
        # Removes the cells containg graph data.
        contents = cell_remover(contents, "\"GRAPH\\n\"")
        # Removes the cells containg graph related text.
        contents = cell_remover(contents, "GRAPH_TEXT")
        # removes graph lines from cell
        contents = line_remover(contents, "GRAPH_LINE")

    def remove_checklist_line_from_template(contents):
        contents = line_remover(contents, "CHECKLIST_LINE")
        contents = cell_remover(contents, "CHECKLIST_INFORMATION")
    # Creates a list of all nominal frames from the nominal checklist.
    if checklist_file_path != "data" or checklist_file_path != "":
        try:
            frame_list_nominal = flight_data(checklist_file_path,
                                             "Checklists nominal.xlsx")
            frame_list_emergency = flight_data(checklist_file_path,
                                               "Checklists Emergency.xlsx")
            print('Looking for checklists')
            filtered_frame_nominal = checklist_finder(frame_list_nominal,
                                                      flight_number,
                                                      flight_date)
            # Filters the data to get just the required data.
            filtered_frame_emergency = checklist_finder(frame_list_emergency,
                                                        flight_number,
                                                        flight_date)
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
                remove_checklist_line_from_template(contents)
            else:
                contents = contents.replace("CHECKLIST_LINE", "")
        except ValueError:
            remove_checklist_line_from_template(contents)
            print("Checklist not found")
        except PermissionError:
            remove_checklist_line_from_template(contents)
            print("Unable to open the checklist, check that it is not open \
                  else where")
        except UnboundLocalError:
            remove_checklist_line_from_template(contents)
            print("Check checklists contain all of the relevant information")
        except FileNotFoundError:
            remove_checklist_line_from_template(contents)
            print("Checklist not found, check that the checklist exists and is\
                  in the correct location")
    else:
        remove_checklist_line_from_template(contents)
    # Checks to see if the start and end time are in the correct format
    hours_valid = True
    try:
        int(start_time_hours)
    except ValueError:
        hours_valid = False
    try:
        int(end_time_hours)
    except ValueError:
        hours_valid = False
    # Checks to see if ICAO code is valid, if not then the Metar information is
    # removed
    if (ICAO_airfield != "data" or ICAO_airfield != "")\
            and hours_valid is True:
        # Retrieves METAR data.
        metar_data = METAR_finder(ICAO_airfield, str(flight_date)[:4],
                                  str(flight_date)[4:6], str(flight_date)[6:8],
                                  str(flight_date)[4:6], str(flight_date)[6:8],
                                  start_time_hours, end_time_hours,
                                  metar_file_path)
        # Checks to see if METAR data is avilable.
        if len(metar_data) != 0:
            # Checks to see if the quota limit has been reached.
            if metar_data[0] == "Quota limit reached.":
                # If the limit has been reached then it puts in a line of code
                # to re-try when the quota limit has been reached.
                contents = METAR_quota_returner(contents,
                                                flight_log_file_name_header +
                                                str(flight_date) + " " +
                                                str(flight_number) +
                                                ".ipynb", ICAO_airfield,
                                                str(flight_date)[:4],
                                                str(flight_date)[4:6],
                                                str(flight_date)[6:8],
                                                str(flight_date)[4:6],
                                                str(flight_date)[6:8],
                                                start_time_hours,
                                                end_time_hours,
                                                metar_file_path,
                                                replace_key="METAR_" +
                                                "INFORMATION")
                # Replaces JFLTS METAR text with nothing if data is available.
                contents = contents.replace("METAR_LINE", "")
                contents = contents.replace("METAR_TEXT", "")
            else:
                # Includes METAR data into the contents.
                contents = METAR_returner(metar_data, contents,
                                          int(str(flight_date)[4:6]),
                                          int(str(flight_date)[:4]),
                                          replace_key="METAR_INFORMATION")
                # Replaces JFLTS METAR text with nothing if data is available.
                contents = contents.replace("METAR_LINE", "")
                contents = contents.replace("METAR_TEXT", "")
        else:
            contents = no_METAR_returner(ICAO_airfield, str(flight_date)[:4],
                                         str(flight_date)[4:6],
                                         str(flight_date)[6:8],
                                         str(flight_date)[4:6],
                                         str(flight_date)[6:8],
                                         start_time_hours, end_time_hours,
                                         contents,
                                         replace_key="METAR_INFORMATION")
            # Replaces JFLTS METAR text with nothing if data is available
            contents = contents.replace("METAR_LINE", "")
            contents = contents.replace("METAR_TEXT", "")
    else:
        # Removes METAR related cells and lines.
        contents = cell_remover(contents, "METAR_INFORMATION")
        contents = line_remover(contents, "METAR_LINE")
        contents = cell_remover(contents, "METAR_TEXT")
    # Creates a new flight log from the contents
    flight_log_creator(contents, flight_log_file_path, flight_date,
                       flight_number, flight_log_file_name_header)
    print('Flight log maker finished')


def flight_data(file_path, file_name):
    """This imports the data excel using pandas"""
    # Excel file.
    file_path_with_name = file_path + os.sep + file_name
    # Tidies up the base path for python.
    file_path_with_name = file_path_with_name.replace(os.sep, "/")
    file = pd.ExcelFile(file_path_with_name)
    # Finds list of sheet names.
    sheet_list = file.sheet_names
    # Creates empty list for frames.
    frame_list = []
    # Extracts data from each sheet.
    for sheet in sheet_list:
        frame = pd.read_excel(file_path + os.sep + file_name, sheet_name=sheet)
        frame_list.append(frame)
    return(frame_list)


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
    flight_number_filtered = \
        checklist_frame[checklist_frame[flight_number_column] == flight_number]
    # Converts index to list
    index = flight_number_filtered.index.values.tolist()
    # Creates a list with times
    times = flight_number_filtered[flight_number_filtered.columns[2]].tolist()
    # Creates an empty list of rows to be removed
    Rows = []
    # For the items in index, the time is converted to the same format as the
    # date and if they are not equal, then that index is added to rows to be
    # removed.
    for a in range(len(index)):
        if str(times[a]).split(" ")[0].replace("-", "") == str(date):
            Rows.append(index[a])
    # Removes row if its index equals a row to be removed.
    filtered_frame = flight_number_filtered[
            flight_number_filtered.index.isin(Rows)]
    return(filtered_frame)


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
    checklists_actioned =\
        filtered_nominal[filtered_nominal.columns[5]].tolist()
    checklist_actioned_by =\
        filtered_nominal[filtered_nominal.columns[4]].tolist()
    end_date_time = filtered_nominal[filtered_nominal.columns[2]].tolist()
    start_date_time = filtered_nominal[filtered_nominal.columns[1]].tolist()
    damage = filtered_nominal["Damage"].tolist()
    battery = filtered_nominal["Battery Voltages"].tolist()
    notes = filtered_nominal["Notes"].tolist()
    b = 0
    for column in filtered_nominal.columns:
        # If a column contains the word Checklist and the word checklist
        # has not previously appeared then b is set to 1 to stop the loops
        # and record the frame.
        if "Checklist (VER " in column:
            b = 1
            break
        if b != 0:
            break
    version_completed = filtered_nominal[column].tolist()
    if len(version_completed) != 0:
        version_completed = \
            str(version_completed[0]).replace("Completed (", "")
        version_completed = \
            str(version_completed).replace(")", "")
    # Emergency Checklist
    filtered_emergency = filtered_frame_emergency
    emergency_checklists_actioned =\
        filtered_emergency[filtered_emergency.columns[5]].tolist()
    emergency_checklist_actioned_by =\
        filtered_emergency[filtered_emergency.columns[4]].tolist()
    emergency_end_date_time =\
        filtered_emergency[filtered_emergency.columns[2]].tolist()
    emergency_start_date_time =\
        filtered_emergency[filtered_emergency.columns[1]].tolist()
    emergency_notes = filtered_emergency["Notes"].tolist()
    for column in filtered_emergency.columns:
        # If a columnn contains the word Checklist (VER  and the word
        # checklist has not previously appeared then b is set to 1 to stop the
        # loops and record the frame.
        if "Checklist (VER " in column:
            b = 1
            break
    version_completed_emergency = filtered_emergency[column].tolist()
    if len(version_completed_emergency) != 0:
        version_completed_emergency = \
            str(version_completed_emergency[0]).replace("Completed (", "")
        version_completed_emergency = \
            str(version_completed_emergency).replace(")", "")
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
            text = "\n    \"The " + checklists_actioned[index] +\
                " was actioned by " + checklist_actioned_by[index] +\
                " starting at " + str(start_date_time[index]) + " and " +\
                "ending at " + str(end_date_time[index]) + "."
            # If there are notes, then append them to the text with the
            # following text.
            if str(notes[index]) != "nan":
                text += " The notes recorded on this checklist were: " +\
                    "<i>" + notes[index]
            # Adds full stop to end if required.
            if text[-1:] != "." and text[-1:] != "!" and text[-1:] != "?":
                text += "."
            text += "</i>"
            # If there is damage recorded, then append them to the text with
            # the following text.
            if str(damage[index]) != "nan":
                text = text + " Damage was reported on this flight as/" +\
                    " the report can be found at: <i>" + damage[index]
                # Adds full stop to end if required.
                if text[-1:] != "." and text[-1:] != "!" and text[-1:] != "?":
                    text += "."
                text += "</i>"
            if str(battery[index]) != "nan":
                text = text + " The Battery voltages of each battery are/ " +\
                    "can be found at: <i>" + battery[index]
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
            text = "\n    \"The " + emergency_checklists_actioned[index] +\
                " was actioned by " + emergency_checklist_actioned_by[index] +\
                " starting at " + str(emergency_start_date_time[index]) +\
                " and ending at " + str(emergency_end_date_time[index]) + "."
            # If there are notes, then append them to the text with the
            # following text.
            if str(emergency_notes[index]) != "nan":
                text += " The notes recorded on this checklist were: " +\
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
    # Thie creates a list to contain the recorded flight duration and who
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
            if str(column[index]) != "nan" and \
                    str(column[index]).lower != "Null":
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
            if str(column[index]) != "nan" and \
                    str(column[index]).lower != "Null":
                flight_duration_data.append(
                        [emergency_checklist_actioned_by[index],
                         column[index]])
    if len(flight_duration_data) == 0:
        # FDI stands for Flight Duration Info and it is there to show if the
        # Flight Duration was recorded.
        FDI = 0
    else:
        FDI = 1
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
                    a = 0
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
                text = text + "and " + checklist_and_number[-1:][0][0] +\
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
                    text = text + " and " + number_greater_than_1[0][0] +\
                        " was actioned " + str(number_greater_than_1[0][1]) +\
                        " times."
                # if it does not then it loops through the lists.
                else:
                    if len(number_greater_than_1) != 0:
                        text = text + " and "
                        for repeat in number_greater_than_1[:-1]:
                            text = text + repeat[0] + " was actioned " +\
                                str(repeat[1]) + " times, "
                            # This removes the Oxford comma.
                        text = text[:-2] + " "
                        text = text + "and " +\
                            number_greater_than_1[-1:][0][0] +\
                            " was actioned " +\
                            str(number_greater_than_1[-1:][0][1]) + " times."
                    else:
                        text = text + "."
        # This else is for it it only has one item
        else:
            # Checks if that checklist is repeated multiple times and then it
            # will state how many times it was repeated.
            if checklist_and_number[0][1] == 1:
                text = "The " + checklist_and_number[0][0] + checklist_item[1]\
                    + " checklist was actioned."
            else:
                text = "The " + checklist_and_number[0][0] + checklist_item[1]\
                    + " checklist was actioned " +\
                    str(checklist_and_number[0][1]) + " times."
        text_list.append(text)
    # Checks to see if the emergency checklist is available and replaces it
    # with a blank space if it is not
    if FDI == 1:
        flight_duration_text = ""
        for data in flight_duration_data:
            flight_duration_text = flight_duration_text + "\n    \"The " + \
                "flight Duration was recorded as / can be found at: " + \
                str(data[1]) + ", this data was recorded by " +\
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
        version_completed_text = "\n    \"The checklist " +\
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
        "    \"<h1>Checklist Information</h1><a class=\\\"anchor\\\" " +\
        "id=\\\"Checklist-Information\\\"></a>\\n\",\n    \"\\n\",\n" + \
        "    \"" + text_list[0] + " " + text_list[1] + "\\n\",\n    " +\
        "\"\\n\"," + flight_duration_text + checklist_actioned_text +\
        emergency_checklist_actioned_text + version_completed_text +\
        version_completed_emergency_text +\
        "\n   ]\n" + \
        "  },"
    # Checks to see if there is any relavent checklists and removes them if
    # there is not.
    checklist_exist = True
    if filtered_frame_nominal.shape[0] == 0 and \
            filtered_frame_emergency.shape[0] == 0:
        checklist_information = ""
        checklist_exist = False
    contents = contents.replace(checklist_replacement, checklist_information)
    return(contents, checklist_exist)


def contents_opener(file_path, file_name):
    """This code opens a specified file and returns the contents"""
    # opens file
    file = open(file_path + os.sep + file_name, "r")
    # Extracts contents.
    contents = file.read()
    # Closes the file.
    file.close()
    return(contents)


def flight_data_and_axis(new_frames):
    """Returns list of lists with the following structure [[data source,
    [name, unit, data],[name, unit, data]], [data source, [name, unit, data],
    [name, unit, data]]]."""
    print('Importing flight data')
    # Creates an empty list for all the data.
    values_list = []
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
                # c is used to indicate that there is a unit. If c is equal to
                #  1 then there is no unit for that particular measure.
                c = 0
            else:
                if len(column.split("_")) == 4:
                    # This indicates that there are no units for that
                    # particular value.
                    c = 1
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
                            # a space as a seperator
                            if a <= 0:
                                name += " "
                    else:
                        if letter != "_" and c == 0:
                            unit = unit + letter
                        elif c == 1:
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
                    unit = unit + denominator[0] + "$^{-" +\
                           str(denominator[1]) + "}$"
            data_lists.append([name, unit, y])
        values_list.append(data_lists)
    return(values_list)


def flight_log_graph_contents_replacer(contents):
    """Values list is from the function flight_data_and_axis."""
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
        # Creates an infinite loop used to find the end of that particualar
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
            # Sets line to equal the line at that particlar index.
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
        line = "  {\n   \"cell_type\": \"code\",\n" +\
            "   \"execution_count\": null,\n   \"metadata\": {},\n" +\
            "   \"outputs\": [],\n   \"source\": [\n" +\
            "   \"x_limits=[\\\"x_min\\\", \\\"x_max\\\"]\\n\",\n" +\
            "   \"y_limits=[\\\"y_min\\\", \\\"y_max\\\"]\\n\",\n" +\
            "   \"graph_function(["
        for axis in data:
            line += axis + ", "
        line = line[:-2]
        line += "], values_list, x_limits, y_limits)\"\n   ]\n  }"
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
        # Replaces exisitng text with graphs
        contents = contents.replace(old_cell_text, notebook_lines[index] + end)
        # increments the index so that the next set of data is included.
        index += 1
    return(contents)


def graph_function(plot_information, values_list, x_limits=["x_min", "x_max"],
                   y_limits=["y_min", "y_max"]):
    """ Goes through graph data, finds source and gets required data from
    values. plot information structure, [x, name, data_source]"""
    # List of data to plot returns plot data which has structure:
    # [axis, [data_source, column]]
    plot_data = []
    for data in plot_information:
        values_list_index = 0
        # sets value_found to a defult of False
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
                        # If it is then it sets it to be the referance unit
                        referance_x_unit = xy_data[1][1]
                        # Sets a referance heading for the x data.
                        referance_x_heading = xy_data[1][0]
                        first_x_unit = False
                    else:
                        # Sets the unit of the next item
                        unit = xy_data[1][1]
                        # Sets the heading of the next item
                        heading = xy_data[1][0]
                        if referance_x_unit == unit and \
                                referance_x_heading == heading:
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
                    # If it is then it sets it to be the referance unit.
                    referance_y_unit = xy_data[1][1]
                    first_y_unit = False
                else:
                    # If this is the second y value found.
                    unit = xy_data[1][1]
                    # If the units are constant then plot them together
                    if referance_y_unit == unit:
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
    if plot_info == 2 or plot_info == 3:
        for x_data in x_list:
            # Checks through each y data item.
            for y_data in y_list:
                # if the x and y data have the same source then they can be
                # plottted together
                if x_data[2] == y_data[2]:
                    # Appends which x values and y values that can be plotted
                    # against each other.
                    xy_pairs.append([x_data[1], y_data[1]])
    if plot_info == 1:
        plt.plot(x[2], y[2])
        # plots x name with unit in brackets.
        plt.xlabel(x[0] + " (" + x[1] + ")")
        # plots y name with unit in brackets.
        plt.ylabel(y[0] + " (" + y[1] + ")")
        # plots title for graph.
        title = y[0] + " (" + y[1] + ") plotted against " + x[0] + " (" +\
            x[1] + ")"
    # If y units have the same unit then this will format the graphs as
    # required.
    if plot_info == 2:
        for pair in xy_pairs:
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
        # Plots the title.
        title = text + " plotted against " + xy_pairs[0][0][0]
    # If y units do not have the same unit then this will format the graphs
    # as required.
    if plot_info == 3:
        for pair in xy_pairs:
            # plots x against y values.
            plt.plot(pair[0][2], pair[1][2], label=pair[1][0] +
                     " (" + pair[1][1] + ")")
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
        # Plots the title.
        title = text + " plotted against " + xy_pairs[0][0][0]
    # if plot info is equal to 0 then nothing is returned
    if plot_info == 0:
        return
    # Splits title if its width exceeds 60
    wraped_title = textwrap.wrap(title, width=60)
    # Creates an empty string for the final title
    final_title = ""
    # Goes through each line in the title and joins them together with a new
    # line character between each line.
    for title_line in wraped_title:
        final_title += title_line + "\n"
    # Removes new line at end
    plt.title(final_title[:-1], y=1.05)
    # Checks to see if plot limits have been set for the x values
    if isinstance(x_limits[0], int) and isinstance(x_limits[1], int):
        plt.xlim(x_limits)
    # Checks to see if plot limts have been set for the y values
    if isinstance(y_limits[0], int) and isinstance(y_limits[1], int):
        plt.ylim(y_limits)


def flight_log_multiaxis_graph_contents_replacer(contents):
    """Values list is from the function flight_data_and_axis."""
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
        # Creates an infinite loop used to find the end of that particualr cell
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
            # Sets line to equal the line at that particlar index.
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
            # replace spaces with speach marks for jupyter
            line = line.replace(" ", "\\\", \\\"")
            # If the name has more than one word in it then replace the
            # underscore with a space.
            line = line.replace("_", " ")
            # Appends data to list if it is not set to ignore that row.
            if ignore is True:
                ignore = False
            else:
                graph_list[graph_data_index][axis].append("[\\\"" + line
                                                          + "\\\"]")
        graph_data_index += 1
    notebook_lines = []
    for data in graph_list:
        line = "  {\n   \"cell_type\": \"code\",\n" +\
            "   \"execution_count\": null,\n   \"metadata\": {},\n" +\
            "   \"outputs\": [],\n   \"source\": [\n" +\
            "   \"x_limits=[\\\"x_min\\\", \\\"x_max\\\"]\\n\",\n" +\
            "   \"y_limits_left=[\\\"y_min\\\", \\\"y_max\\\"]\\n\",\n" +\
            "   \"y_limits_right=[\\\"y_min\\\", \\\"y_max\\\"]\\n\",\n" +\
            "   \"legend_location=1\\n\",\n" +\
            "   \"multiaxis_graph_function(["
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
        line += "], values_list, x_limits, y_limits_left, y_limits_right," +\
            " legend_location)\"\n   ]\n  }"
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
        # Replaces exisitng text with graphs
        contents = contents.replace(old_cell_text, notebook_lines[index] + end)
        # increments the index so that the next set of data is included.
        index += 1
    return(contents)


def multiaxis_graph_function(plot_information_left, plot_information_right,
                             values_list, x_limits=["x_min", "x_max"],
                             y_limits_left=["y_min", "y_max"],
                             y_limits_right=["y_min", "y_max"],
                             legend_location=1):
    """ Goes through graph data, finds source and gets required data from
    values. plot information structure, [x, name, data_source], plots data on
    left and right axis as specified as inputs, legend location will specifiy
    where the legend should go"""
    # List of data to plot returns plot data which has structure:
    # [axis, [data_source, column]]
    plot_information = [plot_information_left, plot_information_right]
    plot_list = []
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
                            # If it is then it sets it to be the referance unit
                            referance_x_unit = xy_data[1][1]
                            # Sets a referance heading for the x data.
                            referance_x_heading = xy_data[1][0]
                            first_x_unit = False
                        else:
                            # Sets the unit of the next item
                            unit = xy_data[1][1]
                            # Sets the heading of the next item
                            heading = xy_data[1][0]
                            if referance_x_unit == unit and \
                                    referance_x_heading == heading:
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
                        # If it is then it sets it to be the referance unit.
                        referance_y_unit = xy_data[1][1]
                        first_y_unit = False
                    else:
                        # If this is the second y value found.
                        unit = xy_data[1][1]
                        # If the units are constant then plot them together
                        if referance_y_unit == unit:
                            plot_info = 2
                        else:
                            plot_info = 3
                            break
        # Apends data to list
        plot_list.append([plot_info, plot_data])
    # Plots data
    graph, axis_1 = plt.subplots()
    # Renames data to make it compatible with older code.
    plot_info = plot_list[0][0]
    plot_data = plot_list[0][1]
    # Counts how many lines are being drawn.
    line_count = 0
    # Creates a list with a label in it for the axis.
    lines = axis_1.plot([], [], " ", label="Left hand axis")
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
            # plottted together
            if x_data[2] == y_data[2]:
                # Appends which x values and y values that can be plotted
                # against each other.
                xy_pairs.append([x_data[1], y_data[1]])
    if plot_info == 1:
        line = axis_1.plot(x[2], y[2], label=y[0] + " (" + y[1] + ")",
                           color="C" + str(line_count))
        # plots x name with unit in brackets.
        axis_1.set_xlabel(x[0] + " (" + x[1] + ")")
        # plots y name with unit in brackets.
        axis_1.set_ylabel(y[0] + " (" + y[1] + ")")
        # plots title for graph.
        title = y[0] + " (" + y[1] + ") plotted against " + x[0] + " (" +\
            x[1] + ")"
        line_count = 1
        lines += line
    # If y units have the same unit then this will format the graphs as
    # required.
    if plot_info == 2:
        for pair in xy_pairs:
            # plots x against y values.
            line = axis_1.plot(pair[0][2], pair[1][2], label=pair[1][0] +
                               " (" + pair[1][1] + ")",
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
            text += " and " + xy_pairs[len(xy_pairs) - 1][1][0]
        # Plots Legend.
        # Plots Y label.
        axis_1.set_ylabel(text + " (" + xy_pairs[0][1][1] + ")")
        # Plots X label.
        axis_1.set_xlabel(xy_pairs[0][0][0] + " (" + xy_pairs[0][0][1] + ")")
        # Plots the title.
        title = text + " plotted against " + xy_pairs[0][0][0]
    # If y units do not have the same unit then this will format the graphs
    # as required.
    if plot_info == 3:
        for pair in xy_pairs:
            # plots x against y values.
            line = axis_1.plot(pair[0][2], pair[1][2], label=pair[1][0] +
                               " (" + pair[1][1] + ")",
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
            text += " and " + xy_pairs[len(xy_pairs) - 1][1][0]
        # Plots X label.
        axis_1.set_xlabel(xy_pairs[0][0][0] + " (" + xy_pairs[0][0][1] + ")")
        # Plots the title.
        title = text + " plotted against " + xy_pairs[0][0][0]
    # Records plot info for the left axis
    plot_info_left = plot_info
    # Renames data to make it compatible with older code.
    plot_info = plot_list[1][0]
    plot_data = plot_list[1][1]
    axis_2 = axis_1.twinx()
    # If there is Y axis data for the Right hand axis then plot the label
    if plot_info != 0:
        lines += axis_2.plot([], [], " ", label="Right hand axis")
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
            # plottted together
            if x_data[2] == y_data[2]:
                # Appends which x values and y values that can be plotted
                # against each other.
                xy_pairs.append([x_data[1], y_data[1]])
    if plot_info == 1:
        line = axis_2.plot(x[2], y[2], label=y[0] + " (" + y[1] + ")",
                           color="C" + str(line_count))
        # Increments line count
        line_count += 1
        # Appends current line to list of lines.
        lines += line
        # plots y name with unit in brackets.
        axis_2.set_ylabel(y[0] + " (" + y[1] + ")")
        # plots title for graph.
        text = y[0] + " (" + y[1] + ") plotted against " + x[0] + " (" +\
            x[1] + ")"
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
            text += " and " + xy_pairs[len(xy_pairs) - 1][1][0]
        # Plots Y label.
        axis_2.set_ylabel(text + " (" + xy_pairs[0][1][1] + ")")
        # Plots X label.
        axis_2.set_xlabel(xy_pairs[0][0][0] + " (" + xy_pairs[0][0][1] + ")")
    # If y units do not have the same unit then this will format the graphs
    # as required.
    if plot_info == 3:
        for pair in xy_pairs:
            # plots x against y values.
            line = axis_2.plot(pair[0][2], pair[1][2], label=pair[1][0] + " ("
                               + pair[1][1] + ")", color="C" + str(line_count))
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
            text += " and " + xy_pairs[len(xy_pairs) - 1][1][0]
        # Plots X label.
        axis_2.set_xlabel(xy_pairs[0][0][0] + " (" + xy_pairs[0][0][1] + ")")
    # If there is no valid data then return nothing.
    if plot_info == 0 and plot_info_left == 0:
        plt.close()
        return
    if plot_info != 0 and plot_info_left != 0:
        # Plots the title.
        full_title = title + " and " + text + " plotted against " +\
            xy_pairs[0][0][0]
    elif plot_info == 0:
        # Plots the title.
        full_title = title
        # Hides right axis if data is missing.
        axis_2.set_yticks([])
    else:
        # Creates a title.
        full_title = text + " plotted against " +\
            xy_pairs[0][0][0]
        # Hides left axis if data is missing.
        axis_1.set_yticks([])
    # Splits title if its width exceeds 60
    wraped_title = textwrap.wrap(full_title, width=60)
    # Creates an empty string for the final title
    final_title = ""
    # Goes through each line in the title and joins them together with a new
    # line character between each line.
    for title_line in wraped_title:
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
    # Checks to see if plot limits have been set for the x values
    if isinstance(x_limits[0], int) and isinstance(x_limits[1], int):
        axis_1.set_xlim(x_limits)
    # Checks to see if plot limts have been set for the y values on the left
    # axis.
    if isinstance(y_limits_left[0], int) and isinstance(y_limits_left[1], int):
        axis_1.set_ylim(y_limits_left)
        # Checks to see if plot limts have been set for the y values on the
        # right axis.
    if isinstance(y_limits_right[0], int) and \
            isinstance(y_limits_right[1], int):
        axis_2.set_ylim(y_limits_right)


def cell_remover(contents, key):
    """This function will remove the cells that contain a specific key
    and ensure that the last cell has the correct comma at the end."""
    # splits contents into lines.
    lines = contents.split("\n")
    line_list = []
    # Finds the line numbers that contain the graph key word
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
        # Replaces cells containg the word graph with blank text
        contents = contents.replace(old_cell_text, "")
    lines = contents.split("\n")
    # Finds the line numbers that contain the kernel spec key word
    for index in range(len(lines)):
        if "\"kernelspec\": {" in lines[index]:
            kernel_spec_index = index
            # Ends check as it has found what is looking for
            break
    # Sets kernal_spec_text to contain nothing.
    kernel_spec_text = ""
    # Goes throught the lines after the lines containing kernal_spec
    for line in reversed(lines[:kernel_spec_index]):
        # If the last line is as it should be then return the contents.
        if line == "  }":
            break
        else:
            # If the end of the lastr cell contains a comma then it must be
            # removed.
            if line == "  },":
                # Removes comma from the end of the last cell.
                contents = contents.replace("  },\n" + kernel_spec_text,
                                            "  }\n" + kernel_spec_text)
                # Once comma is removed then break out of the for loop and
                # return the contents.
                break
            else:
                # If not at the end then more lines are appeneded.
                kernel_spec_text = line + "\n" + kernel_spec_text
    # Returns the new contents.
    return(contents)


def line_remover(contents, key):
    """ This function will remove and lines that contain a specific key."""
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
    return(contents)


def flight_log_creator(contents, file_path, date, flight_number,
                       file_name_header="Flight Log "):
    """This creates or overwrites a file with the name file_name_header date
     flight_number.ipynb  and fills the file with the
    contents provided as an input."""
    # Creates file with name
    print('Creating new flight log')
    file = open(file_path + os.sep + file_name_header + str(date) + " " +
                str(flight_number) + ".ipynb", "w+")
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
    for frame in (frame_list):
        # Empty list to be populated by columns that contain time more than
        # once.
        frame_columns_list = []
        # Columns is a list of columns.
        columns = frame_list[a].columns
        # Increments a
        a = a + 1
        # Loops through each column to see if it contains the word time.
        for column in columns:
            # Checks to see if the word time appears in the column.
            if "time" in column.lower():
                # If time appears then it is apended to the list time_columns.
                time_columns.append(column)
                # Divides column by 1*10^6 to return it to seconds.
                frame[column] = frame[column].div(10**6)
                # Adds columns in this data frame that contain the word time to
                # a list.
                frame_columns_list.append(column)
                # appends replacment column to dictionary.
                renamed_time_columns[column] = (column.replace("_US_", "_s_"))
        # Creates a copy of the columns to delete parts from.
        frame_copy = frame.copy()
        # The variable b will be used to divide the list.
        b = 0
        # This variable is used to trigger the appending of the data frames to
        # the list data frames.
        c = 0
        # Checks through each of the columns.
        for column in columns:
            if b == 0:
                frame_duplicate = frame_copy.copy()
                b = 1
                # Checks to see if column is a time column.
                for time_column in time_columns:
                    if column == time_column:
                        c = 1
                # Removes frames
                frame_copy = frame_copy.drop(labels=column, axis=1)
                if c == 1:
                    # Removes columns from the frame_duplicate list
                    for column_drop in frame_copy.columns:
                        frame_duplicate = frame_duplicate.\
                                          drop(labels=column_drop, axis=1)
                    # Checks if time appers in column being checked.
                    new_frames.append(frame_duplicate)
                    b = c = 0
            else:
                # Checks to see if column is a time column.
                for time_column in time_columns:
                    if column == time_column:
                        c = 1
                # Removes frames
                frame_copy = frame_copy.drop(labels=column, axis=1)
                if c == 1:
                    # Removes columns from the frame_duplicate list
                    for column_drop in frame_copy.columns:
                        frame_duplicate = frame_duplicate.\
                                          drop(labels=column_drop, axis=1)
                    # Checks if time appers in column being checked.
                    new_frames.append(frame_duplicate)
                    b = c = 0
    # Creates a blank list for the frames with the seconds unit fixed.
    arranged_frames = []
    # Renames columns and changes the units of time from US (microseconds) to s
    for frame in new_frames:
        # Replaces the unit
        frame.rename(columns=renamed_time_columns, inplace=True)
        # Appends the frame.
        arranged_frames.append(frame)
    return(arranged_frames)


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
        # Emptys rev_file_extension.
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
    return(required_files)


def date_and_flight_number(frames):
    """This function finds the date and flight number from the headings in
    the list of frames provided by the function flight data"""
    # Starts at the data frame (first sheet).
    for frame in frames:
        # Scans through the columns.
        for column in frame.columns:
            # Splits column name by the underscore.
            lines = column.split("_")
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
                return(date, flight_number)


def METAR_finder(location, year, month, day, month_end, day_end,
                 start_time_hours, end_time_hours, metar_file_path=""):
    """This grabs URL if it is not already available."""
    # End time to actual end time in hours
    print('Checking for METAR')
    end_time_hours = str(int(end_time_hours) - 1)
    # Checks to see if a metar file path is available.
    if metar_file_path != "" or metar_file_path != "data":
        # Creates a list of all the files in the METAR_file_path
        file_list = os.listdir(metar_file_path)
        # Creates a file name based off input data
        file_name = "METAR_" + location + "_" + year + month + day +\
            "_" + year + month_end + day_end + "_" +\
            start_time_hours + "_" + end_time_hours
        # Goes through each of the files.
        for file in file_list:
            # Checks to see if there is a chached file that matches the current
            # requested data.
            if file_name in file:
                # Opens file.
                metar_file = open(metar_file_path + os.sep + file_name +
                                  ".txt", "r")
                # Extracts Data.
                metar_data = metar_file.read()
                # Closes file.
                metar_file.close()
                metar_data = metar_data.split("\n")
                return(metar_data)
    URL = "https://www.ogimet.com/display_metars2.php?lang=en&lugar=" +\
        location + "&tipo=ALL&ord=REV&nil=SI&fmt=html&ano=" + year +\
        "&mes=" + month + "&day=" + day + "&hora=" + start_time_hours +\
        "&anof=" + year + "&mesf=" + month_end + "&dayf=" + day_end +\
        "&horaf=" + end_time_hours + "&minf=59&send=send"
    request_data = get(URL)
    # Splits the data by line.
    metar_html = request_data.text.split("\n")
    # Goes through each of the lines of data.
    index = 0
    line_index = []
    # Goes through each of the lines.
    for line in metar_html:
        # If quota limit reached
        if "#Sorry, Your quota limit for "\
                in line:
            # Return the text, Quota limit reached if the quota limit has been
            # reached.
            return(["Quota limit reached.", location, year, month, day,
                    month_end, day_end, start_time_hours, end_time_hours,
                    metar_file_path])
        # Checks to see if the lines contain that particular string.
        if "<td><font size=\"-1\"><b><pre>METAR" in line:
            # Appends data to line index.
            line_index.append(index)
        # Increments the line index.
        index += 1
    # Creates a blank list for the metar data.
    metar_data = []
    # Goes through the list and replaces HTML at the begining and end of the
    # string.
    for index in line_index:
        # Repalces HTML at the begining of the text.
        data = metar_html[index].replace("<td><font size=\"-1\"><b><pre>", "")
        # Replaces HTML at the end of the text.
        data = data.replace("=</pre></b></font></td>", "")
        # Appends data to a list.
        metar_data.append(data)
    # Creates an empty string to be appended to.
    text = ""
    # Goes through metars.
    for metar in metar_data:
        # Appends metar and new line.
        text += metar + "\n"
    # If there is no METAR data then the empty list is returned.
    if len(metar_data) == 0:
        return(metar_data)
    # Adds URL to end
    text += URL
    # Creates a new text file to locally store and append the data to.
    metar_file = open(metar_file_path + os.sep + file_name + ".txt", "w+")
    # Extracts contents.
    metar_file.write(text)
    # Closes the file.
    metar_file.close()
    # Returns the list.
    metar_data.append(URL)
    return(metar_data)


def METAR_returner(metar_data, contents, month, year,
                   replace_key="METAR_INFORMATION"):
    """Replaces the key word in a cell with METAR information from the day"""
    # finds the locations that the metars were recorded from.
    metar_text = "    \"The METARs for " +\
        str(Metar.Metar(metar_data[0], month=month, year=year))[9:13] +\
        " were:\\n\",\n    \"\\n\",\n"
    # Goes through the metars and creates a list of metars from that day.
    for metar in metar_data[:-1]:
        # Uses the metar function to get the data from the metar and display
        # the data labeled nicely
        metar_text += "    \"" +\
            str(Metar.Metar(metar[6:], month=month, year=year))[14:].replace(
                    "\n", "\\n\",\n    \"\\n\",\n    \"") +\
            "\\n\",\n     \"<br><br><br><br>\\n\",\n"
    # Adds the metar data to the text file.
    metar_text += "    \"This METAR data was from:" + metar_data[-1] + "\""
    # Creates replacement text for the METAR key.
    metar_replacement = "\n  {\n " + \
        "  \"cell_type\": \"markdown\",\n" + \
        "   \"metadata\": {},\n" + \
        "   \"source\": [\n" + \
        "    \"" + replace_key + "\"\n" + \
        "   ]\n" + \
        "  },"
    # Creates some text to replace the cell.
    metar_information = "  {\n " + \
        "  \"cell_type\": \"markdown\",\n" + \
        "   \"metadata\": {},\n" + \
        "   \"source\": [\n" + \
        "    \"<h1>METAR Information</h1><a class=\\\"anchor\\\" " +\
        "id=\\\"METAR-Information\\\"></a>\\n\",\n    \"\\n\",\n" + \
        metar_text +\
        "\n   ]\n" + \
        "  },"
    contents = contents.replace(metar_replacement, metar_information)
    return(contents)


def no_METAR_returner(location, year, month, day, month_end, day_end,
                      start_time_hours, end_time_hours, contents,
                      replace_key="METAR_INFORMATION"):
    """Replaces the key word in a cell with note that no METAR information was
    available from the day"""
    # finds the locations that the metars were recorded from.
    metar_text = "    \"No METARs for " + location + " for the date " + day +\
        month + year + " from a starting time of " + start_time_hours +\
        ":00 and an end time of " + str(int(end_time_hours) - 1) + ":59.\\n\""
    # Creates replacement text for the METAR key.
    metar_replacement = "\n  {\n " + \
        "  \"cell_type\": \"markdown\",\n" + \
        "   \"metadata\": {},\n" + \
        "   \"source\": [\n" + \
        "    \"" + replace_key + "\"\n" + \
        "   ]\n" + \
        "  },"
    # Creates some text to replace the cell.
    metar_information = "  {\n " + \
        "  \"cell_type\": \"markdown\",\n" + \
        "   \"metadata\": {},\n" + \
        "   \"source\": [\n" + \
        "    \"<h1>Metar Information <a class=\\\"anchor\\\" " +\
        "id=\\\"Metar-Information\\\"></a></h1>\\n\",\n    \"\\n\",\n" + \
        metar_text +\
        "\n   ]\n" + \
        "  },"
    contents = contents.replace(metar_replacement, metar_information)
    return(contents)


def METAR_quota_returner(contents, file_name, location, year,
                         month, day, month_end, day_end, start_time_hours,
                         end_time_hours, metar_file_path,
                         replace_key="METAR_INFORMATION"):
    """Puts METAR_replacer function in to replace METAR_INFORMATION cell"""
    """Replaces the key word in a cell with METAR incofrmation from the day"""
    # Creates replacement text for the METAR key.
    metar_replacement = "\n  {\n " + \
        "  \"cell_type\": \"markdown\",\n" + \
        "   \"metadata\": {},\n" + \
        "   \"source\": [\n" + \
        "    \"" + replace_key + "\"\n" + \
        "   ]\n" + \
        "  },"
    # Creates some text to replace the cell.
    metar_information = "  {\n " + \
        "  \"cell_type\": \"code\",\n" + \
        "   \"execution_count\": null,\n" + \
        "   \"metadata\": {},\n" + \
        "   \"outputs\": [],\n" + \
        "   \"source\": [\n" + \
        "    \"# METAR REPLACER\\n\",\n    \"\\n\",\n" + \
        "    \"METAR_replacer(os.getcwd(), \\\"" + file_name + "\\\", \\\"" +\
        location + "\\\", \\\"" + year + "\\\", \\\"" + month + "\\\", \\\"" +\
        day + "\\\", \\\"" + month_end + "\\\", \\\"" + day_end +\
        "\\\", \\\"" + start_time_hours + "\\\", \\\"" + end_time_hours +\
        "\\\", \\\"" + metar_file_path.replace("\\", jupyter_sep) +\
        "\\\")\"\n   ]\n" + \
        "  },"
    contents = contents.replace(metar_replacement, metar_information)
    return(contents)


def METAR_replacer(file_path, file_name, location, year, month, day,
                   month_end, day_end, start_time_hours, end_time_hours,
                   metar_file_path):
    """This will replace the code with the METAR data if available."""
    # finds metar data.
    metar_data = METAR_finder(location, year, month, day, month_end, day_end,
                              start_time_hours, end_time_hours,
                              metar_file_path)
    if len(metar_data) == 0:
        return("No METAR data found.")
    if metar_data[0] == "Quota limit reached.":
        return("Sorry, Quota limit has been reached, try again later.")
    # Opens contents
    contents = contents_opener(file_path, file_name)
    # Splits contents into lines
    lines = contents.split("\n")
    # Creates an index
    index = 0
    # Creates an index showing where the last open curly bracket was.
    bracket_index = 0
    for line in lines:
        if "# METAR REPLACER" in line:
            break
        if line == "  {":
            # Records postion of last bracket.
            bracket_index = index
        index += 1
    lines = cell_remover(contents, "# METAR REPLACER").split("\n")
    # Lines for the METAR_returner code to replace.
    metar_information = "\n  {\n " + \
                        "  \"cell_type\": \"markdown\",\n" + \
                        "   \"metadata\": {},\n" + \
                        "   \"source\": [\n" + \
                        "    \"METAR_INFORMATION\"\n" + \
                        "   ]\n" + \
                        "  },"
    # Inserts metar_information into lines at the point where the curly bracket
    # was for the code.
    # Test
    lines.insert(bracket_index, metar_information)
    contents = ""
    # Reassembles contents from lines
    for line in lines:
        contents += line + "\n"
    contents = METAR_returner(metar_data, contents,
                              replace_key="METAR_INFORMATION")
    file = open(file_path + os.sep + file_name, "w+")
    # Extracts contents.
    file.write(contents)
    # Closes the file.
    file.close()
    return("METAR data successfully included, please press save then reload" +
           " and the METAR data should appear in place of this cell.")


def arduino_micro_frame(flight_data_file_path, arduino_flight_data_name):
    """Takes file path of arduino micro flight data and returns a pandas
    data frame."""
    # Creates file path from graph file path and file name
    file_path = flight_data_file_path + os.sep + arduino_flight_data_name
    if arduino_flight_data_name == "" or flight_data_file_path == "":
        return(pd.DataFrame())
    # Reads CSV
    frame = pd.read_csv(file_path)
    return(frame)