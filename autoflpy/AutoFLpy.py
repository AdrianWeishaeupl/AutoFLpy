"""
This modules allows for the running of the log to xls converter and the
automatic flight log generator.
"""

__author__ = "Adrian Weishaeupl"

from autoflpy.log_to_xls import *
from autoflpy.flight_log_code import *
import autoflpy.name_generator as name_generator
import os
import json
import autoflpy.flight_log_code as flight_log_code
import autoflpy.log_to_xls as log_to_xls
import autoflpy.nearest_ICAO_finder as nearest_ICAO_finder

"""
TODO:
    Finish writing unittests.
    Find why the METAR information displays the incorrect date/data.
    Move utility files into a util folder.
    Remove the code from the Jupyter template and move it out of sight.
    Find a way that the code can recognise if the nearest airfield has weather
        data.
    Find a way of allowing custom weather data to be added - add it into the
        input file.
    Fix checklist integration into notebook.
    Get the code to make directories in the working directory os.mkdir
    Examples in the example folder
"""


def autoflpy(input_file='Input File.json'):
    # Finds the file path from where this code is being run.
    base_path = os.path.join(os.path.dirname(__file__), "data") + os.sep
    # Tidies up the base path for python.
    base_path = base_path.replace(os.sep, "/")
    # Reads the test_input_file information
    with open(base_path + input_file) as file:
        data = json.load(file)
    default_storage_path = (base_path[:-14] + 'data' + os.sep).replace(os.sep,
                                                                       "/")
    # Sets  variables from the input file to be used.
    # If no log file path has been entered, go to the standard log path.
    if data["log_to_xls_input"]["log_file_path"] != "":
        log_file_path = (data["log_to_xls_input"][
            "log_file_path"] + os.sep + data["log_to_xls_input"][
            "log_file_name"]).replace(os.sep, "/")
    else:
        log_file_path = (default_storage_path + 'log files' +
                         os.sep + data["log_to_xls_input"]["log_file_name"]
                         ).replace(os.sep, "/")
    print(log_file_path)
    name_converter_file_path = base_path + 'Name converter list.txt'
    data_sources_path = base_path + 'Data sources.txt'
    # If no excel data file path has been entered, go to the standard path.
    if data["log_to_xls_input"]["excel_data_file_path"] != "":
        excel_file_path = (data["log_to_xls_input"][
            "excel_data_file_path"]).replace(os.sep, "/")
    else:
        excel_file_path = (default_storage_path + 'excel data'
                           ).replace(os.sep, "/")
    flight_date = data["log_to_xls_input"]["date"]
    flight_number = data["log_to_xls_input"]["flight_number"]
    name_generator.excel_file_name_updater(flight_date, flight_number)
    # Generates an appropriate file name
    excel_file_name = name_generator.generated_file_name

    # Runs the xls converter
    log_to_xls.log_reader(log_file_path,
                          name_converter_file_path,
                          data_sources_path,
                          excel_file_path,
                          excel_file_name,
                          flight_date,
                          flight_number)

    # Assigns variables - checks if any information is entered into the input
    # file for the directories before resorting to the default directory.
    if data["flight_log_generator_input"]["template_file_path"] != "":
        template_file_path = (data["flight_log_generator_input"][
            "template_file_path"]).replace(os.sep, "/")
    else:
        template_file_path = base_path
    if data["flight_log_generator_input"]["template_file_name"] != "":
        template_file_name = data["flight_log_generator_input"][
            "template_file_name"]
    else:
        template_file_name = 'Default Template (Full Summary).ipynb'
    if data["flight_log_generator_input"]["flight_log_destination"] != "":
        flight_log_file_path = data["flight_log_generator_input"][
                "flight_log_destination"]
    else:
        flight_log_file_path = default_storage_path + 'flight logs generated'
    flight_data_file_path = (excel_file_path + os.sep).replace(os.sep, "/")
    flight_data_file_name = excel_file_name + ".xls"
    if data["flight_log_generator_input"][
            "arduino_flight_data_file_path"] != "":
        arduino_flight_data_file_path = data[
            "flight_log_generator_input"]["arduino_flight_data_file_path"]
    else:
        arduino_flight_data_file_path = default_storage_path + 'arduino data'
    arduino_flight_data_name = data["flight_log_generator_input"][
            "arduino_flight_data_name"]
    flight_log_file_name_header = "Generated flight log"
    if data["flight_log_generator_input"][
            "checklist_data_file_path"] != "":
        checklist_file_path = data[
            "flight_log_generator_input"]["checklist_data_file_path"]
    else:
        checklist_file_path = default_storage_path
    log_code_version = "flight_log_code"
    start_time_hours = data["flight_log_generator_input"]["start_time_hours"]
    end_time_hours = data["flight_log_generator_input"]["end_time_hours"]
    if data["flight_log_generator_input"][
            "metar_file_path"] != "":
        metar_file_path = data[
            "flight_log_generator_input"]["metar_file_path"]
    else:
        metar_file_path = default_storage_path + 'metar file storage'
    # Finds the nearest airfield for METAR information
    ICAO_airfield = nearest_ICAO_finder.icao_finder(flight_data_file_path,
                                                    flight_data_file_name)

    # Runs the flight log generator
    flight_log_code.flight_log_maker(template_file_path,
                                     template_file_name,
                                     flight_log_file_path,
                                     flight_data_file_path,
                                     flight_data_file_name,
                                     arduino_flight_data_file_path,
                                     arduino_flight_data_name,
                                     flight_date,
                                     flight_number,
                                     flight_log_file_name_header,
                                     checklist_file_path,
                                     log_code_version,
                                     ICAO_airfield,
                                     start_time_hours,
                                     end_time_hours,
                                     metar_file_path)


if __name__ == "__main__":
    autoflpy()
