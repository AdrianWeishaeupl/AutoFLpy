import os
from requests import get
from autoflpy.util.text_manipulation import contents_opener, cell_remover

try:
    from metar import Metar as mtr
except ImportError:
    print('METAR module not installed correctly')
    raise Exception('Please install the metar module before continuing.'
                    ' BASH command: $ pip install metar')

# Checks to see if os.sep is \\
if os.sep == "\\":
    # If it is then it sets the jupyter sep to be \\\\\\\\ eight slashes so \\
    jupyter_sep = "\\\\\\\\"
else:
    jupyter_sep = "/"


def metar_finder(location, year, month, day, month_end, day_end,
                 start_time_hours, end_time_hours, metar_file_path=""):
    """This grabs url if it is not already available.

    If the METAR is already cached, the cached file is returned

    If the quota limit has been reached, returns a list of variables:
    ["Quota limit reached.", location, year, month, day,
        month_end, day_end, start_time_hours, end_time_hours,
        metar_file_path]

    If no METAR data is found, returns an empty string

    If METAR data is called from the API, return data with url at the end
    """
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
    # TODO: find a way of shortening the URL
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


def metar_returner(metar_data, contents, months, years, number_of_flights,
                   replace_key="METAR_INFORMATION"):
    """Replaces the key word in a cell with METAR information from the day"""
    # finds the locations that the metars were recorded from.

    metar_text = ""
    for flight in range(number_of_flights):
        if "https://" not in metar_data[flight]:
            metar_text += "    \"The METARs for " + \
                          str(mtr.Metar(metar_data[flight], month=months[flight], year=years[flight]))[9:13] + \
                          " were:\\n\",\n    \"\\n\",\n"
            # Goes through the metars and creates a list of metars from that day.
        for metar in metar_data[:-1]:
            # Uses the metar function to get the data from the metar and display
            # the data labeled nicely
            metar_text += "    \"" + \
                          str(mtr.Metar(metar[6:], month=months[flight], year=years[flight]
                                        ))[14:].replace(
                              "\n", "\\n\",\n    \"\\n\",\n    \"") + \
                          "\\n\",\n     \"<br><br><br><br>\\n\",\n"
        # Adds the metar data to the text file.
        # TODO: shorten hyperlink (metar_data[-1])
        metar_text += "    \"This METAR data was from:" + metar_data[-1] + "\\n\"," + "\"\\n\",\n"

    metar_text = metar_text[:-7]  # Removes the "," + "\"\\n\",\n from the last line for json compatibility

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
                        "    \"<h2>METAR Information</h2><a class=\\\"anchor\\\" " + \
                        "id=\\\"METAR-Information\\\"></a>\\n\",\n    \"\\n\",\n" + \
                        metar_text + \
                        "\n   ]\n" + \
                        "  },"
    contents = contents.replace(metar_replacement, metar_information)
    return contents


def no_metar_returner(location, dates, end_dates,
                      start_time_hours, end_time_hours, contents, number_of_flights,
                      replace_key="METAR_INFORMATION"):
    """Replaces the key word in a cell with note that no METAR information was
    available from the day"""
    metar_text = ""
    for flight in range(number_of_flights):
        year = str(dates[flight])[:4]
        year_end = str(end_dates[flight])[:4]
        month = str(dates[flight])[4:6]
        month_end = str(end_dates[flight])[4:6]
        day = str(dates[flight])[6:8]
        day_end = str(end_dates[flight])[6:8]
        # finds the locations that the metars were recorded from.
        metar_text += "    \"No METARs for " + str(location[flight]) + " for the date " + day + "/"+ \
                      month + "/" + year + " to the date " + day_end + "/" + \
                      month_end + "/" + year_end + \
                      " from a starting time of " + str(start_time_hours[flight]) + ":00 and an end time of " + \
                      str(int(end_time_hours[flight]) - 1) + ":59.\\n\",\n"
    metar_text = metar_text[:-2]  # Removes "," from the end for json validity.
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
                         end_time_hours, metar_file_path, number_of_flights,
                         replace_key="METAR_INFORMATION"):
    """Puts metar_replacer function in to replace METAR_INFORMATION cell"""
    """Replaces the key word in a cell with METAR information from the day"""
    # TODO: Make this work for dictionary inputs
    metar_information = ""
    # Creates replacement text for the METAR key.
    metar_replacement = "\n  {\n " + \
                        "  \"cell_type\": \"markdown\",\n" + \
                        "   \"metadata\": {},\n" + \
                        "   \"source\": [\n" + \
                        "    \"" + replace_key + "\"\n" + \
                        "   ]\n" + \
                        "  },"
    # Creates some text to replace the cell.
    for flight in range(number_of_flights):
        metar_information += "  {\n " + \
                             "  \"cell_type\": \"code\",\n" + \
                             "   \"execution_count\": null,\n" + \
                             "   \"metadata\": {},\n" + \
                             "   \"outputs\": [],\n" + \
                             "   \"source\": [\n" + \
                             "    \"# METAR REPLACER{}\\n\",\n    \"\\n\",\n".format(flight) + \
                             "    \"metar_replacer(os.getcwd(), \\\"" + file_name + "\\\", \\\"" + \
                             location[flight] + "\\\", \\\"" + str(year[flight]) + "\\\", \\\"" + \
                             str(month[flight]) + "\\\", \\\"" + \
                             str(day[flight]) + "\\\", \\\"" + str(month_end[flight]) + "\\\", \\\"" +\
                             str(day_end[flight]) + \
                             "\\\", \\\"" + str(start_time_hours[flight]) + "\\\", \\\"" +\
                             str(end_time_hours[flight]) + "\\\", \\\"" + str(flight) + \
                             "\\\", \\\"" + metar_file_path.replace("\\", jupyter_sep) + \
                             "\\\")\"\n   ]\n" + \
                             "  },"
    contents = contents.replace(metar_replacement, metar_information)
    return contents


def metar_replacer(file_path, file_name, location, year, month, day,
                   month_end, day_end, start_time_hours, end_time_hours, flight,
                   metar_file_path):
    """This will replace the code with the METAR data if available."""
    # TODO: Known bug: if only one metar_replacer is run in the workbook when multiple are present, the un-run cells
    #  will be removed without any metar information being entered.
    # Finds metar data.
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
        if "# METAR REPLACER{}".format(flight) in line:
            break
        if line == "  {":
            # Records position of last bracket.
            bracket_index = index
        index += 1
    lines = cell_remover(contents, "# METAR REPLACER{}".format(flight)).split("\n")
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
    contents = metar_returner(metar_data, contents, [int(month)], [int(year)], 1,
                              replace_key="METAR_INFORMATION")
    file = open(file_path + os.sep + file_name, "w+")
    # Extracts contents.
    file.write(contents)
    # Closes the file.
    file.close()
    return ("METAR data successfully included, please press save then reload" +
            " and the METAR data should appear in place of this cell.")
