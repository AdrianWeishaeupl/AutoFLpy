"""
This modules allows for the running of the log to xlsx converter and the
automatic flight log generator.
"""

__author__ = "Adrian Weishaeupl"

import autoflpy.util.name_generator as name_generator
import os
import json
import autoflpy.util.flight_log_code as flight_log_code
import autoflpy.util.log_to_xlsx as log_to_xlsx
import autoflpy.util.nearest_ICAO_finder as nearest_ICAO_finder
from shutil import copyfile

"""
TODO:
    Calculate wind speed/vector/plot.
    Add flight duration from vibration data.
    Add a 3D map image to summarise flight.
    Option to display time in UTC or time after flight start.
"""


def autoflpy(input_file='Input_File.json', include_metar=False, run_log_to_xlsx=True):
    """autoflpy serves as the user interface for flight report generation.

    Upon first time running of the script, sample data will be used to create a sample flight report for the user to
    look at for inspiration.

    A folder structure containing the "Input_File.json" and base file paths will also be created.
    The user can then complete the "Input_File.json" with appropriate information and analyse their own flight data.

    Folder structure generated:

    user_files
        * csv_data                  Contains sample CSV data. User data in the form of a csv file can be added here.
        * excel_file_path		    Contains excel files generated from the log files.
        * flight_logs_generated		Contains the generated flight reports.
        * log_files					Contains the user input flight data in the .log format.
        * METAR_storage				This acts as a database for the METAR data.

    arguments:
        include_metar=False
            If set to True, METAR information from the nearest airport will be collected and added to the log. This only
            works when data from a single flight is being analysed.

        run_log_to_xlsx=True
            If set to False, xlsx files will not be generated which will save time. Do this if these files have already
            been created. It will cause errors if the xlsx files are not present or in the wrong directory.
    """
    # Finds the file path from where this code is being run.
    base_path = os.path.join(os.path.dirname(__file__), "data") + os.sep
    # Tidies up the base path for python.
    base_path = base_path

    # Sets the default storage location in the working directory.
    default_storage_path = str((os.getcwd() + os.sep + 'user_files' + os.sep
                                ))

    # Copies the standard input file into the working directory
    if os.path.exists(default_storage_path + input_file) is False:
        os.makedirs(default_storage_path, exist_ok=True)
        print('Storage directory made in: {}'.format(default_storage_path))
        copyfile(base_path + input_file, default_storage_path + input_file)
    else:
        pass

    data_sources_path = default_storage_path + 'Data_sources.txt'
    if os.path.exists(data_sources_path) is False:
        copyfile(base_path + 'Data_sources.txt', data_sources_path)
    else:
        pass
    # Copies the template input file into the current working directory
    input_template_file = 'Input_File_Template.json'
    if os.path.exists(default_storage_path + input_template_file) is False:
        copyfile(base_path + input_template_file, default_storage_path +
                 input_template_file)
    else:
        pass

    # Reads the test_input_file information.
    with open(default_storage_path + input_file) as file:
        data = json.load(file)

    # Sets  variables from the input file to be used.
    # If no log file path has been entered, go to the standard log path.
    log_file_paths = []
    if data["log_to_xlsx_input"]["log_file_path"] != "" and os.path.exists(
      data["log_to_xlsx_input"]["log_file_path"]) is True:
        for file in data["log_to_xlsx_input"]["log_file_name"].replace(" ", "").split(","):
            log_file_paths.append(data["log_to_xlsx_input"][
                                      "log_file_path"] + os.sep + file)
    else:
        # Creates a new directory to look for files.
        log_file_base_path = (default_storage_path + "log_files" + os.sep
                              )
        for file in data["log_to_xlsx_input"]["log_file_name"].replace(" ", "").split(","):
            log_file_paths.append(log_file_base_path + os.sep + file)
        try:
            os.makedirs(log_file_base_path)
            # Raises error and gives advice on how to continue.
            raise FileNotFoundError('No log file directory was entered. A new directory has been'
                                    ' made.')
        except OSError:
            print('Log file path found.')
            # Copies the example data file into the log storage
            copyfile(base_path + 'test_log_to_xlsx.log', log_file_base_path +
                     'test_log_to_xlsx.log')

    name_converter_file_path = base_path + 'Name_converter_list.txt'
    # If no excel data file path has been entered, go to the standard path.
    if data["log_to_xlsx_input"]["excel_data_file_path"] != "" and \
        os.path.exists(
            data["log_to_xlsx_input"]["excel_data_file_path"]) is True:
        excel_file_path = (data["log_to_xlsx_input"][
            "excel_data_file_path"])
    else:
        # Makes a directory in the current working path to be used.
        excel_file_path = default_storage_path + "excel_file_path"
        try:
            os.makedirs(excel_file_path)
        except OSError:
            print("Excel folder found. Will use this folder to store generated"
                  " xlsx files.")
    # Formats the flight dates and flight numbers as lists and checks their length against the length of flight_dates
    flight_dates = str(data["log_to_xlsx_input"]["date"]).replace(" ", "").split(",")
    flight_numbers = flight_log_code.multi_string_data_formatter(data["log_to_xlsx_input"]["flight_number"],
                                                                 flight_dates, "flight_numbers")
    # Generates an appropriate file name
    excel_file_names = name_generator.excel_file_name_updater(flight_dates, flight_numbers)

    # Imports custom weather data entered into the input file
    try:
        weather_data_multi = data["weather_data"]
    except KeyError:
        print("'weather_data' has not been entered.")
        weather_data_multi = {}

    # Imports custom runway data entered into the input file
    try:
        runway_data_multi = data["runway_data"]
    except KeyError:
        print("'runway_data' has not been entered.")
        runway_data_multi = {}

    # Imports custom aircraft data entered in the input file
    try:
        aircraft_data_multi = data["aircraft_data"]
    except KeyError:
        print("'aircraft_data' has not been entered.")
        aircraft_data_multi = {}

    # Formats the weather data into several separate dictionaries
    weather_data_lists = flight_log_code.multi_dictionary_data_formatter(
        weather_data_multi, flight_dates, "weather_data")
    # Formats the runway data into several separate dictionaries
    runway_data_lists = flight_log_code.multi_dictionary_data_formatter(
        runway_data_multi, flight_dates, "runway_data")
    aircraft_data_lists = flight_log_code.multi_dictionary_data_formatter(
        aircraft_data_multi, flight_dates, "aircraft_data")

    if run_log_to_xlsx is True:
        # Runs the xlsx converter
        log_to_xlsx.log_reader_multi(log_file_paths,
                                     name_converter_file_path,
                                     data_sources_path,
                                     excel_file_path,
                                     excel_file_names,
                                     flight_dates,
                                     flight_numbers,
                                     weather_data_lists,
                                     runway_data_lists,
                                     aircraft_data_lists)
    else:
        print("log_to_xlsx has been disabled. This will cause errors if .xlsx data has not been generated previously or"
              " is not in the correct folder.")

    start_times_hours = flight_log_code.multi_string_data_formatter(
        data["flight_log_generator_input"]["start_time_hours"], flight_dates, "start_time_hours")
    end_times_hours = flight_log_code.multi_string_data_formatter(
        data["flight_log_generator_input"]["end_time_hours"], flight_dates, "end_time_hours")
    csv_flight_data_names = flight_log_code.multi_string_data_formatter(
        data["flight_log_generator_input"]["csv_flight_data_name"], flight_dates, "csv_flight_data_name")
    flight_data_file_names = []
    for name in excel_file_names:
        flight_data_file_names.append(str(name) + ".xlsx")

    # Assigns variables - checks if any information is entered into the input
    # file for the directories before creating new directories in the current
    # working directory.
    if data["flight_log_generator_input"]["template_file_path"] != "" and \
        os.path.exists(
            data["flight_log_generator_input"]["template_file_path"]) is True:
        template_file_path = (data["flight_log_generator_input"][
            "template_file_path"])
    else:
        template_file_path = default_storage_path
    if data["flight_log_generator_input"]["template_file_name"] != "" and \
        os.path.exists(
            template_file_path +
            data["flight_log_generator_input"]["template_file_name"]) is True:
        template_file_name = data["flight_log_generator_input"][
            "template_file_name"]
    else:
        template_file_name = 'Default_Template_(Full_Summary).ipynb'
        print('Using default template')
        # Checks that the file is not already present
        if os.path.exists(default_storage_path + template_file_name) is False:
            # Copies the default template into the default storage directory
            copyfile(base_path + template_file_name, default_storage_path +
                     template_file_name)
    if data["flight_log_generator_input"]["flight_log_destination"] != "" and \
        os.path.exists(
            data["flight_log_generator_input"][
                "flight_log_destination"]) is True:
        flight_log_file_path = data["flight_log_generator_input"][
            "flight_log_destination"]
    else:
        # Makes a directory in the current working path to be used.
        flight_log_file_path = default_storage_path + "flight_logs_generated"
        try:
            os.makedirs(flight_log_file_path)
        except OSError:
            print("Flight log folder found. Will use this folder to store "
                  "generated flight log files.")
    flight_data_file_path = (excel_file_path + os.sep)
    if data["flight_log_generator_input"][
        "csv_flight_data_file_path"] != "" and \
        os.path.exists(data["flight_log_generator_input"]
                       ["csv_flight_data_file_path"]) is True:
        csv_flight_data_file_path = data[
            "flight_log_generator_input"]["csv_flight_data_file_path"]
    else:
        # Makes a directory in the current working path to be used.
        csv_flight_data_file_path = (default_storage_path + "csv_flight_data" + os.sep)
        try:
            os.makedirs(csv_flight_data_file_path)
        except OSError:
            print('CSV flight data folder found.')
        # Copies the csv test data into the new file path
        copyfile(base_path + 'test_csv.CSV', csv_flight_data_file_path
                 + 'test_csv.CSV')

    flight_log_file_name_header = "Flight_report_"

    if data["flight_log_generator_input"][
        "metar_file_path"] != "" and \
        os.path.exists(
            data["flight_log_generator_input"]["metar_file_path"]) is True:
        metar_file_path = data[
            "flight_log_generator_input"]["metar_file_path"]
    else:
        # Makes a directory in the current working path to be used.
        metar_file_path = (default_storage_path + "METAR_storage" +
                           os.sep)
        try:
            os.makedirs(metar_file_path)
        except OSError:
            print('METAR storage folder found.')
    # Creates images folder for the logo
    images_path = (default_storage_path + 'images' + os.sep
                   )
    try:
        os.makedirs(images_path)
    except OSError:
        print('Images folder found.')
        # Copies the test logo into the new file path if it is not already
        # present
    if os.path.exists(images_path + 'Your_logo_file_name_here.png') is False:
        copyfile(base_path + 'Your_logo_file_name_here.png',
                 images_path + 'Your_logo_file_name_here.png')

    # Excludes METAR for multiple flights
    if include_metar is True:
        if len(flight_dates) > 1:
            include_metar = False
            print("Metar is disabled for multiple flights")
        else:
            include_metar = True

    # Finds the nearest airfield for METAR information
    if include_metar is True:
        icao_airfields = nearest_ICAO_finder.multi_icao_finder(flight_data_file_path,
                                                               flight_data_file_names, excel_file_names)
    else:
        # ICAO airfields not required
        icao_airfields = []

    # Runs the flight log generator
    flight_log_code.flight_log_maker(template_file_path,
                                     template_file_name,
                                     flight_log_file_path,
                                     flight_data_file_path,
                                     flight_data_file_names,
                                     csv_flight_data_file_path,
                                     csv_flight_data_names,
                                     flight_dates,
                                     flight_numbers,
                                     flight_log_file_name_header,
                                     icao_airfields,
                                     start_times_hours,
                                     end_times_hours,
                                     metar_file_path,
                                     weather_data_lists,
                                     runway_data_lists,
                                     include_metar)


if __name__ == "__main__":
    autoflpy(run_log_to_xlsx=True, include_metar=True)
