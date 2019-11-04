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

if __name__ == "__main__":

    # Finds the file path from where this code is being run.
    base_path = os.getcwd()[:-9] + os.sep + 'data' + os.sep
    # Tidies up the base path for python.
    base_path = base_path.replace(os.sep, "/")
    # Reads the test_input_file information
    with open(base_path + 'Input File.json') as file:
        data = json.load(file)
    # Sets  variables from the input file to be used.
    log_file_path = base_path + data["log_to_xls_input"][
            "log_file_path"] + os.sep + data["log_to_xls_input"][
            "log_file_name"]
    name_converter_file_path = base_path + data[
            "log_to_xls_input"]["name_converter_file_path"]
    data_sources_path = base_path + data[
            "log_to_xls_input"]["data_sources_file_path"]
    excel_file_path = base_path + data[
            "log_to_xls_input"]["excel_data_file_path"]
    name_generator.excel_file_name_updater(data[
            "log_to_xls_input"]["date"], data[
            "log_to_xls_input"]["flight_number"])
    # Generates an appropriate file name
    excel_file_name = name_generator.generated_file_name
    flight_date = data["log_to_xls_input"]["date"]
    flight_number = data["log_to_xls_input"]["flight_number"]
    # Runs the xls converter
    log_to_xls.log_reader(log_file_path,
                          name_converter_file_path,
                          data_sources_path,
                          excel_file_path,
                          excel_file_name,
                          flight_date,
                          flight_number)

    # Assigns variables
    template_file_path = base_path
    template_file_name = data["flight_log_generator_input"][
            "template_file_path"]
    flight_log_file_path = base_path + data["flight_log_generator_input"][
            "flight_log_destination"]
    # NOTE: Need to find out what this is.
    flight_data_file_path = excel_file_path
    flight_data_file_name = excel_file_name + ".xls"
    arduino_flight_data_file_path = base_path + data[
            "flight_log_generator_input"]["arduino_flight_data_file_path"]
    arduino_flight_data_name = data["flight_log_generator_input"][
            "arduino_flight_data_name"]
    flight_log_file_name_header = "Generated flight log"
    checklist_file_path = base_path
    log_code_version = "flight_log_code"
    ICAO_airfield = data["flight_log_generator_input"]["icao_code"]
    start_time_hours = data["flight_log_generator_input"]["start_time_hours"]
    end_time_hours = data["flight_log_generator_input"]["end_time_hours"]
    metar_file_path = base_path + data["flight_log_generator_input"][
            "metar_file_path"]

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
   