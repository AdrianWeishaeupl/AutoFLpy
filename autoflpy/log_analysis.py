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
    Find a way that the code can recognise if the nearest airfield has weather
        data.
    Throttle as a %??
    Axis variables in plots only take round numbers.
    Calculate wind speed/vector/plot.
    Add flight duration from vibration data.
    Add a 3D map image to summarise flight.
    Option to display time in UTC or time after flight start.
    Fix cell removal if no weather/runway information was entered.
DONE:
"""


def autoflpy(input_file='Input_File.json'):
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
    weather_data_multi = data["weather_data"]

    # Imports custom runway data entered into the input file
    runway_data_multi = data["runway_data"]
    # Formats the weather data into several separate dictionaries
    weather_data_lists = flight_log_code.multi_dictionary_data_formatter(
        weather_data_multi, flight_dates, "weather_data")
    # Formats the runway data into several separate dictionaries
    runway_data_lists = flight_log_code.multi_dictionary_data_formatter(
        runway_data_multi, flight_dates, "runway_data")

    # Runs the xlsx converter
    log_to_xlsx.log_reader_multi(log_file_paths,
                                 name_converter_file_path,
                                 data_sources_path,
                                 excel_file_path,
                                 excel_file_names,
                                 flight_dates,
                                 flight_numbers,
                                 weather_data_lists,
                                 runway_data_lists)

    start_times_hours = flight_log_code.multi_string_data_formatter(
        data["flight_log_generator_input"]["start_time_hours"], flight_dates, "start_time_hours")
    end_times_hours = flight_log_code.multi_string_data_formatter(
        data["flight_log_generator_input"]["end_time_hours"], flight_dates, "end_time_hours")
    arduino_flight_data_names = flight_log_code.multi_string_data_formatter(
        data["flight_log_generator_input"]["arduino_flight_data_name"], flight_dates, "arduino_flight_data_name")
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
        "arduino_flight_data_file_path"] != "" and \
        os.path.exists(data["flight_log_generator_input"]
                       ["arduino_flight_data_file_path"]) is True:
        arduino_flight_data_file_path = data[
            "flight_log_generator_input"]["arduino_flight_data_file_path"]
    else:
        # Makes a directory in the current working path to be used.
        arduino_flight_data_file_path = (default_storage_path + "arduino_flight_data" + os.sep
                                         )
        try:
            os.makedirs(arduino_flight_data_file_path)
        except OSError:
            print('Arduino flight data folder found.')
        # Copies the arduino test data into the new file path
        copyfile(base_path + 'test_arduino.CSV', arduino_flight_data_file_path
                 + 'test_arduino.CSV')

    flight_log_file_name_header = "Generated_flight_log_"
    if data["flight_log_generator_input"][
        "checklist_data_file_path"] != "" and \
        os.path.exists(data[
                           "flight_log_generator_input"]["checklist_data_file_path"]) is True:
        checklist_file_path = data[
            "flight_log_generator_input"]["checklist_data_file_path"]
    else:
        # Makes a directory in the current working path to be used.
        checklist_file_path = (default_storage_path + "checklists" + os.sep
                               )
        try:
            os.makedirs(checklist_file_path)
        except OSError:
            print('Checklists folder found.')
        # Checks that the checklists are not already present in the folder
        if os.path.exists(checklist_file_path + 'Checklists_emergency.xlsx'
                          ) is False:
            # Copies sample checklists into the generated folder.
            copyfile(base_path + 'Checklists_emergency.xlsx',
                     checklist_file_path + 'Checklists_emergency.xlsx')
        if os.path.exists(checklist_file_path + 'Checklists_nominal.xlsx'
                          ) is False:
            copyfile(base_path + 'Checklists_nominal.xlsx', checklist_file_path
                     + 'Checklists_nominal.xlsx')
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
    # Finds the nearest airfield for METAR information
    icao_airfields = nearest_ICAO_finder.multi_icao_finder(flight_data_file_path,
                                                           flight_data_file_names, excel_file_names)

    # Runs the flight log generator
    flight_log_code.flight_log_maker(template_file_path,
                                     template_file_name,
                                     flight_log_file_path,
                                     flight_data_file_path,
                                     flight_data_file_names,
                                     arduino_flight_data_file_path,
                                     arduino_flight_data_names,
                                     flight_dates,
                                     flight_numbers,
                                     flight_log_file_name_header,
                                     checklist_file_path,
                                     icao_airfields,
                                     start_times_hours,
                                     end_times_hours,
                                     metar_file_path,
                                     weather_data_lists, runway_data_lists)


if __name__ == "__main__":
    autoflpy()
