# -*- coding: utf-8 -*-
"""
Unit tests for the take_off_detection module
Created on Tue Feb 18 14:53:20 2020

@author: aw6g15
"""

from autoflpy.util.analysis import take_off_detection
import unittest
import os
import sys
import json
from autoflpy.util import flight_log_code


def notebook_sample_code(flight_data_file_path, flight_data_file_name,
                         arduino_data_file_path, arduino_flight_data_name):
    """Sample flight log code for testing purposes"""
    # GRAPH_DATA_IMPORT

    # Creates a base_path to the test files.
    base_path = os.path.dirname(__file__) + os.sep

    # Creates a link to where the code is stored.
    sys.path.append(base_path[:-11])

    # file_path of the flight data.
    # flight_data_file_path = base_path
    # Excel File name
    # flight_data_file_name = "test_xlsx.xlsx"
    # Arduino File name
    # arduino_flight_data_name = "test_arduino.CSV"
    # Arduino Data file path
    # arduino_data_file_path = base_path
    # Excel Sheets
    frame_list = flight_log_code.flight_data(flight_data_file_path,
                                             flight_data_file_name)
    # A list containing the date first and then the flight number
    date_and_flight_number = flight_log_code.date_and_flight_number(frame_list)
    # Retrieves arduino flight data
    arduino_micro_flight_data_frame =\
        flight_log_code.arduino_micro_frame(arduino_data_file_path,
                                            arduino_flight_data_name)
    # Appends arduino frame to flight data from pixhawk
    frame_list.append(arduino_micro_flight_data_frame)
    # Sorts frames by time
    sorted_frames = flight_log_code.flight_data_time_sorter(frame_list)
    # Creates a list of all the values.
    values_list = flight_log_code.flight_data_and_axis(sorted_frames)
    return(frame_list, date_and_flight_number, arduino_micro_flight_data_frame,
           sorted_frames, values_list)


class TestTakeOffDetection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Runs once before any tests
        # Defines the base path
        base_path = os.path.join(os.path.dirname(__file__), "test_files"
                                 ) + os.sep
        # Tidies base path
        base_path = base_path.replace(os.sep, "/")
        # Opens the input file and reads content
        with open(base_path + 'test_Input_File.json') as file:
            data = json.load(file)
        # Defines variables
        flight_data_file_path = base_path
        flight_data_file_name = "test_xlsx.xlsx"
        arduino_flight_data_file_path = base_path + data[
                "flight_log_generator_input"]["arduino_flight_data_file_path"]
        arduino_flight_data_name = data["flight_log_generator_input"
                                        ]["arduino_flight_data_name"]
        # Creates a global variable to be used in the testing
        global notebook_results
        # Populates the global variable
        notebook_results =\
            notebook_sample_code(flight_data_file_path,
                                 flight_data_file_name,
                                 arduino_flight_data_file_path,
                                 arduino_flight_data_name)

    def setUp(self):
        # Defines variables needed
        pass

    def test_take_off_point_finder(self):
        """Tests the take_off_point_finder"""
        # Generates the data
        values_list = notebook_results[-1]

        take_off_time_alt_list = []
        take_off_groundspeed_list = []
        take_off_time_spd_list = []
        sensitivity_list = [0.05, 0.1, 0.2, 0.5, 0.7]

        # Runs the code with different sensitivities
        for sensitivity in sensitivity_list:
            take_off_time_alt, take_off_groundspeed, take_off_time_spd = \
                take_off_detection.take_off_point_finder(values_list, sensitivity, sensitivity)
            take_off_time_alt_list.append(take_off_time_alt)
            take_off_groundspeed_list.append(take_off_groundspeed)
            take_off_time_spd_list.append(take_off_time_spd)

        expected_take_off_time_alt_list = [33.214209, 33.414129, 33.614049, 34.413729, 34.813569]
        expected_take_off_groundspeed_list = [20.248, 21.471999999999998, 22.54, 25.416, 26.299]
        expected_take_off_time_spd_list = [30.813503, 30.813503, 31.014256, 31.414096, 31.614016]

        # Compares the generated values to the expected values
        for item in range(len(sensitivity_list)):
            self.assertEqual(take_off_groundspeed_list[item], expected_take_off_groundspeed_list[item])
            self.assertEqual(take_off_time_alt_list[item], expected_take_off_time_alt_list[item])
            self.assertEqual(take_off_time_spd_list[item], expected_take_off_time_spd_list[item])

    def test_significant_data_change_via_rms_error(self):
        # To be written
        pass


if __name__ == '__main__':
    unittest.main()
