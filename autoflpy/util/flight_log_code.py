import pandas as pd
import os
import pickle as pk
from requests import get
from openpyxl import load_workbook


try:
    from metar import Metar as mtr
except ImportError:
    print('METAR module not installed correctly')
    raise Exception('Please install the metar module before continuing.'
                    ' BASH command: $ pip install metar')


"""
Flight Log Generation Code.
This code takes flight data in the form of an .xlsx document (generated from a
.log file in a previous step in the same Jupyter Notebook) and plots and
formats the data to be displayed using a template .ipynb file.

It also contains the code used to generate the plots.

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
                     flight_data_file_name, arduino_flight_data_file_path,
                     arduino_flight_data_name, flight_date, flight_number,
                     flight_log_file_name_header, checklist_file_path,
                     icao_airfield, start_time_hours, end_time_hours, metar_file_path,
                     weather_data):
    """This code will edit a specified template and return the result that has
    been produced after the substitution of data into the template."""
    print('Starting Flight Log Maker')
    # loads contents_checklist_rm.
    contents = contents_opener(template_file_path, template_file_name)
    # Inserts the date into the contents_checklist_rm.
    contents = contents.replace("FLIGHT_DATE", (str(flight_date)[6:] + "/" +
                                                str(flight_date)[4:6] + "/" +
                                                str(flight_date)[:4]))
    # Inserts the flight number into the contents_checklist_rm.
    contents = contents.replace("FLIGHT_NUMBER", str(flight_number))
    # Checks to see whether there is graph data or arduino data that can be
    # used to plot graphs by checking if the path exists and if the path has a
    # suitable length to that it is not just greater than 1.
    if (os.path.exists(flight_data_file_path + os.sep + flight_data_file_name)
        is True and
        len(flight_data_file_path + os.sep + flight_data_file_name) > 1) \
        or \
        (os.path.exists(arduino_flight_data_file_path + os.sep +
                        arduino_flight_data_name) is True and
         len(arduino_flight_data_file_path + os.sep +
             arduino_flight_data_name) > 1):
        print('Importing xlsx data')
        # Assigns file name based on excel data
        compressed_data_file_path = flight_data_file_path + flight_data_file_name[:-5] + ".pkl"
        # This replaces the file path with the necessary information
        contents = contents.replace("PYTHON_FILE_PATH", "\\\"" +
                                    os.getcwd().replace("\\", jupyter_sep) +
                                    "\\\"")
        # This replaces the file path to the compressed data
        contents = contents.replace("COMPRESSED_DATA_FILE_PATH", "\\\"" +
                                    (compressed_data_file_path
                                     ).replace("\\", jupyter_sep) + "\\\"")
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
    if (icao_airfield != "data" or icao_airfield != "") and hours_valid is True:
        # Retrieves METAR data.
        metar_data = metar_finder(icao_airfield, str(flight_date)[:4],
                                  str(flight_date)[4:6], str(flight_date)[6:8],
                                  str(flight_date)[4:6], str(flight_date)[6:8],
                                  start_time_hours, end_time_hours,
                                  metar_file_path)
        # Checks to see if METAR data is available.
        if len(metar_data) != 0:
            # Checks to see if the quota limit has been reached.
            if metar_data[0] == "Quota limit reached.":
                # If the limit has been reached then it puts in a line of code
                # to re-try when the quota limit has been reached.
                contents = metar_quota_returner(contents,
                                                flight_log_file_name_header +
                                                str(flight_date) + "_" +
                                                str(flight_number) +
                                                ".ipynb", icao_airfield,
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
                # Includes METAR data into the contents_checklist_rm.
                contents = metar_returner(metar_data, contents,
                                          int(str(flight_date)[4:6]),
                                          int(str(flight_date)[:4]),
                                          replace_key="METAR_INFORMATION")
                # Replaces JFLTS METAR text with nothing if data is available.
                contents = contents.replace("METAR_LINE", "")
                contents = contents.replace("METAR_TEXT", "")
        else:
            contents = no_metar_returner(icao_airfield, str(flight_date)[:4],
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

    # Formats weather_data appropriately to be put into the jupyter notebook as text
    weather_information = weather_reader(weather_data)

    if weather_information != "":  # If information is present, add it to the content.
        contents = contents.replace("\"WEATHER_INFORMATION\"", weather_information)
        contents = contents.replace("WEATHER_LINE", "")
        contents = contents.replace("WEATHER_TEXT", "")
    else:
        # Removes Weather related cells and lines.
        contents = cell_remover(contents, "\"WEATHER_INFORMATION\"")
        contents = line_remover(contents, "WEATHER_LINE")
        contents = cell_remover(contents, "WEATHER_TEXT")

    # Creates a new flight log from the contents_checklist_rm
    flight_log_creator(contents, flight_log_file_path, flight_date,
                       flight_number, flight_log_file_name_header)
    print('Pickling data')
    # Compresses the flight data for faster loading
    compile_and_compress(flight_data_file_path, flight_data_file_name,
                         arduino_flight_data_file_path,
                         arduino_flight_data_name, compressed_data_file_path)
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
                            "    \"<h1>Checklist Information</h1><a class=\\\"anchor\\\" " + \
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


def contents_opener(file_path, file_name):
    """This code opens a specified file and returns the contents"""
    # opens file
    file = open(file_path + os.sep + file_name, "r")
    # Extracts contents.
    contents = file.read()
    # Closes the file.
    file.close()
    return contents


def flight_data_and_axis(new_frames):
    """Returns list of lists with the following structure [[data source,
    [name, unit, data],[name, unit, data]], [data source, [name, unit, data],
    [name, unit, data]]]."""
    # TODO: try rewriting this code in a more legible way.
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
    return values_list


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
    # TODO: KEEP AN EYE ON THIS:
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


def flight_log_creator(contents, file_path, date, flight_number,
                       file_name_header="Flight_Log_"):
    """This creates or overwrites a file with the name file_name_header date
     flight_number.ipynb  and fills the file with the
    contents provided as an input."""
    # Creates file with name
    print('Creating new flight log')
    file = open(file_path + os.sep + file_name_header + str(date) + "_" +
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


def metar_finder(location, year, month, day, month_end, day_end,
                 start_time_hours, end_time_hours, metar_file_path=""):
    """This grabs url if it is not already available."""
    # End time to actual end time in hours
    print('Checking for METAR')
    end_time_hours = str(int(end_time_hours) - 1)
    # Checks to see if a metar file path is available.
    file_name = ""
    if metar_file_path != "" or metar_file_path != "data":
        # Creates a list of all the files in the METAR_file_path
        file_list = os.listdir(metar_file_path)
        # Creates a file name based off input data
        file_name = "METAR_" + location + "_" + year + month + day + \
                    "_" + year + month_end + day_end + "_" + \
                    start_time_hours + "_" + end_time_hours
        # Goes through each of the files.
        for file in file_list:
            # Checks to see if there is a cached file that matches the current
            # requested data.
            if file_name in file:
                print('Found cached METAR information')
                # Opens file.
                metar_file = open(metar_file_path + os.sep + file_name +
                                  ".txt", "r")
                # Extracts Data.
                metar_data = metar_file.read()
                # Closes file.
                metar_file.close()
                metar_data = metar_data.split("\n")
                return metar_data
    print('Getting METAR data from API')
    url = "https://www.ogimet.com/display_metars2.php?lang=en&lugar=" + \
          location + "&tipo=ALL&ord=REV&nil=SI&fmt=html&ano=" + year + \
          "&mes=" + month + "&day=" + day + "&hora=" + start_time_hours + \
          "&anof=" + year + "&mesf=" + month_end + "&dayf=" + day_end + \
          "&horaf=" + end_time_hours + "&minf=59&send=send"
    request_data = get(url)
    # Splits the data by line.
    metar_html = request_data.text.split("\n")
    # Goes through each of the lines of data.
    index = 0
    line_index = []
    # Goes through each of the lines.
    for line in metar_html:
        # If quota limit reached
        if "#Sorry, Your quota limit for " in line:
            # Return the text, Quota limit reached if the quota limit has been
            # reached.
            return (["Quota limit reached.", location, year, month, day,
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
    # Goes through the list and replaces HTML at the beginning and end of the
    # string.
    for index in line_index:
        # Replaces HTML at the beginning of the text.
        data = metar_html[index].replace("<td><font size=\"-1\"><b><pre>", "")
        # Replaces HTML at the end of the text.
        data = data.replace("=</pre></b></font></td>", "")
        # Appends data to a list.
        metar_data.append(data)
    # Creates an empty string to be appended to.
    full_text = ""
    # Goes through metars.
    for metar in metar_data:
        # Appends metar and new line.
        full_text += metar + "\n"
    # If there is no METAR data then the empty list is returned.
    if len(metar_data) == 0:
        return metar_data
    # Adds url to end
    full_text += url
    # Creates a new text file to locally store and append the data to.
    metar_file = open(metar_file_path + os.sep + file_name + ".txt", "w+")
    # Extracts contents.
    metar_file.write(full_text)
    # Closes the file.
    metar_file.close()
    # Returns the list.
    metar_data.append(url)
    return metar_data


def metar_returner(metar_data, contents, month, year,
                   replace_key="METAR_INFORMATION"):
    """Replaces the key word in a cell with METAR information from the day"""
    # finds the locations that the metars were recorded from.
    metar_text = "    \"The METARs for " + \
                 str(mtr.Metar(metar_data[0], month=month, year=year))[9:13] + \
                 " were:\\n\",\n    \"\\n\",\n"
    # Goes through the metars and creates a list of metars from that day.
    for metar in metar_data[:-1]:
        # Uses the metar function to get the data from the metar and display
        # the data labeled nicely
        metar_text += "    \"" + \
                      str(mtr.Metar(metar[6:], month=month, year=year
                                    ))[14:].replace(
                          "\n", "\\n\",\n    \"\\n\",\n    \"") + \
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
                        "    \"<h1>METAR Information</h1><a class=\\\"anchor\\\" " + \
                        "id=\\\"METAR-Information\\\"></a>\\n\",\n    \"\\n\",\n" + \
                        metar_text + \
                        "\n   ]\n" + \
                        "  },"
    contents = contents.replace(metar_replacement, metar_information)
    return contents


def no_metar_returner(location, year, month, day, month_end, day_end,
                      start_time_hours, end_time_hours, contents,
                      replace_key="METAR_INFORMATION"):
    """Replaces the key word in a cell with note that no METAR information was
    available from the day"""
    # finds the locations that the metars were recorded from.
    metar_text = "    \"No METARs for " + location + " for the date " + day + \
                 month + year + " to the date " + day_end + month_end + year + " from a starting time of " \
                 + start_time_hours + ":00 and an end time of " + str(int(end_time_hours) - 1) + ":59.\\n\""
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
                        "    \"<h1>Metar Information <a class=\\\"anchor\\\" " + \
                        "id=\\\"Metar-Information\\\"></a></h1>\\n\",\n    \"\\n\",\n" + \
                        metar_text + \
                        "\n   ]\n" + \
                        "  },"
    contents = contents.replace(metar_replacement, metar_information)
    return contents


def metar_quota_returner(contents, file_name, location, year,
                         month, day, month_end, day_end, start_time_hours,
                         end_time_hours, metar_file_path,
                         replace_key="METAR_INFORMATION"):
    """Puts metar_replacer function in to replace METAR_INFORMATION cell"""
    """Replaces the key word in a cell with METAR information from the day"""
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
                        "    \"metar_replacer(os.getcwd(), \\\"" + file_name + "\\\", \\\"" + \
                        location + "\\\", \\\"" + year + "\\\", \\\"" + month + "\\\", \\\"" + \
                        day + "\\\", \\\"" + month_end + "\\\", \\\"" + day_end + \
                        "\\\", \\\"" + start_time_hours + "\\\", \\\"" + end_time_hours + \
                        "\\\", \\\"" + metar_file_path.replace("\\", jupyter_sep) + \
                        "\\\")\"\n   ]\n" + \
                        "  },"
    contents = contents.replace(metar_replacement, metar_information)
    return contents


def metar_replacer(file_path, file_name, location, year, month, day,
                   month_end, day_end, start_time_hours, end_time_hours,
                   metar_file_path):
    """This will replace the code with the METAR data if available."""
    # finds metar data.
    metar_data = metar_finder(location, year, month, day, month_end, day_end,
                              start_time_hours, end_time_hours,
                              metar_file_path)
    if len(metar_data) == 0:
        return "No METAR data found."
    if metar_data[0] == "Quota limit reached.":
        return "Sorry, Quota limit has been reached, try again later."
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
            # Records position of last bracket.
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
    contents = metar_returner(metar_data, contents, int(month), int(year),
                              replace_key="METAR_INFORMATION")
    file = open(file_path + os.sep + file_name, "w+")
    # Extracts contents.
    file.write(contents)
    # Closes the file.
    file.close()
    return ("METAR data successfully included, please press save then reload" +
            " and the METAR data should appear in place of this cell.")


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
    """
    # Excel Sheets
    frame_list = flight_data(flight_data_file_path, flight_data_file_name)
    # Retrieves arduino flight data
    arduino_flight_data_frame = arduino_micro_frame(arduino_data_file_path,
                                                    arduino_data_file_name)
    # Appends arduino frame to flight data from pixhawk
    frame_list.append(arduino_flight_data_frame)
    # Sorts frames by time
    sorted_frames = flight_data_time_sorter(frame_list)
    # Creates a list of all the values.
    values_list = flight_data_and_axis(sorted_frames)
    # Compresses (pickles) the data and saves it in the excel files folder.
    pk.dump(values_list, open(comp_data_file_path, "wb"))
    print('Pickling finished')


def weather_reader(weather_data):
    """Takes a dictionary of weather data and outputs a formatted string"""
    # Splits the dictionary into lists of values and keys
    weather_keys = list(weather_data.keys())
    weather_values = list(weather_data.values())
    try:
        text = ""

        units = []
        names = []
        # Removes the _ from the names and separates the units from the variable names
        for key in weather_keys:
            units.append(str(key).split("_")[-1])
            names.append(str(key).split("_")[:-1])

        # Joins up variable names in case they are two words
        joined_names = []
        for name_array in names:
            name = ""
            for part in name_array:
                name += part + " "
            joined_names.append(name)

        joined_names, units, weather_values = zip(*sorted(zip(
            joined_names, units, weather_values)))  # Sort alphabetically

        # Adds any non empty values to the text string
        for data_item in range(len(weather_keys)):
            if weather_values[data_item] != "":
                text += "\"" + str(joined_names[data_item]) + \
                        ": " + str(weather_values[data_item]) + " " + str(units[data_item]) \
                        + "\\n\",  \"\\n\", \n   "

        text += "\"\\n\""

    except ValueError:
        print("Weather data not entered or in an incorrect format in the Input_File.json. "
              "Format should be \"variable_unit\": \"value\"")
        text = ""

    return text
