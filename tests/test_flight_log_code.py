# -*- coding: utf-8 -*-
"""
Unit tests for the flight_log_code.py.

@author Adrian Weishaeupl (aw6g15@soton.ac.uk)
"""

import unittest
import os
import json
import sys
from autoflpy.util import flight_log_code
from datetime import datetime
from autoflpy.util import nearest_ICAO_finder
from autoflpy.util.testing.check_str_in_content import *


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
    arduino_micro_flight_data_frame = \
        flight_log_code.arduino_micro_frame(arduino_data_file_path,
                                            arduino_flight_data_name)
    # Appends arduino frame to flight data from pixhawk
    frame_list.append(arduino_micro_flight_data_frame)
    # Sorts frames by time
    sorted_frames = flight_log_code.flight_data_time_sorter(frame_list)
    # Creates a list of all the values.
    values_list = flight_log_code.flight_data_and_axis(sorted_frames)
    return (frame_list, date_and_flight_number, arduino_micro_flight_data_frame,
            sorted_frames, values_list)


class TestFlightLogCode(unittest.TestCase):

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
        notebook_results = \
            notebook_sample_code(flight_data_file_path,
                                 flight_data_file_name,
                                 arduino_flight_data_file_path,
                                 arduino_flight_data_name)

    def setUp(self):
        # Sets up all of the test variables and locations to be used
        # throughout.
        self.base_path = os.path.join(os.path.dirname(__file__),
                                      "test_files") + os.sep
        self.base_path = self.base_path.replace(os.sep, "/")
        # Imports data from template.
        with open(self.base_path + 'test_Input_File.json') as file:
            self.data = json.load(file)
        self.flight_number = self.data["log_to_xlsx_input"]["flight_number"].replace(" ", "").split(",")
        self.flight_date = self.data["log_to_xlsx_input"]["date"].replace(" ", "").split(",")
        self.template_file_path = self.base_path
        self.template_file_name = self.data["flight_log_generator_input"][
            "template_file_name"]
        self.flight_log_file_path = self.base_path + self.data[
            "flight_log_generator_input"]["flight_log_destination"]
        self.flight_data_file_path = self.base_path  # Path to xlsx file
        self.flight_data_file_name = "test_xlsx.xlsx"
        self.flight_data_file_name_list = ["test_xlsx.xlsx"]
        self.arduino_flight_data_file_path = self.base_path + self.data[
            "flight_log_generator_input"]["arduino_flight_data_file_path"]
        self.arduino_flight_data_name = self.data["flight_log_generator_input"
        ]["arduino_flight_data_name"].replace(" ", "").split(",")
        self.flight_log_file_name_header = "test_generated_flight_log"
        self.checklist_file_path = self.base_path
        self.start_time_hours = self.data["flight_log_generator_input"][
            "start_time_hours"].replace(" ", "").split(",")
        self.end_time_hours = self.data["flight_log_generator_input"][
            "end_time_hours"].replace(" ", "").split(",")
        self.metar_file_path = self.base_path + self.data[
            "flight_log_generator_input"]["metar_file_path"]
        self.comp_data_file_path = self.flight_data_file_path + "test_xlsx.pkl"
        self.weather_data = flight_log_code.multi_dictionary_data_formatter(self.data["weather_data"], self.flight_date
                                                                            , "weather_data")
        self.weather_data_dict = self.data["weather_data"]
        self.runway_data = flight_log_code.multi_dictionary_data_formatter(self.data["runway_data"], self.flight_date,
                                                                           "runway_data")
        self.runway_data_dict = self.data["runway_data"]

    def tearDown(self):
        # Removes generated flight log.
        base_path = os.path.join(os.path.dirname(__file__),
                                 "test_files") + os.sep
        generated_file_names = [base_path + "test_generated_flight_logtest_xlsx.ipynb", base_path +
                               "test_generated_flight_log20190123_2.ipynb"]
        for item in range(len(generated_file_names)):
            if os.path.exists(generated_file_names[item]):
                os.remove(generated_file_names[item])

        # Removes pickled data.
        pickle_file_names = [base_path + "test_xlsx.pkl"]
        for item in range(len(pickle_file_names)):
            if os.path.exists(pickle_file_names[item]):
                os.remove(pickle_file_names[item])

    def test_flight_log_maker(self):
        self.ICAO_airfield = nearest_ICAO_finder.icao_finder(
            self.flight_data_file_path,
            self.flight_data_file_name)
        flight_log_code.flight_log_maker(self.template_file_path,
                                         self.template_file_name,
                                         self.flight_log_file_path,
                                         self.flight_data_file_path,
                                         self.flight_data_file_name_list,
                                         self.arduino_flight_data_file_path,
                                         self.arduino_flight_data_name,
                                         self.flight_date,
                                         self.flight_number,
                                         self.flight_log_file_name_header,
                                         self.checklist_file_path,
                                         self.ICAO_airfield,
                                         self.start_time_hours,
                                         self.end_time_hours,
                                         self.metar_file_path,
                                         self.weather_data,
                                         self.runway_data)
        # This code tests the flight_log_maker function.
        # First, check that a file has been created.
        test_flight_log_file_path = self.base_path + 'test_generated_flight_logtest_xlsx.ipynb'
        if os.path.exists(test_flight_log_file_path) is True:
            file_exists = True
        else:
            file_exists = False
        self.assertTrue(file_exists)
        # Checks that the file was recently created.
        filetime = os.stat(test_flight_log_file_path)
        # Finds the time since the file has been created.
        time_diff = datetime.now() - datetime.fromtimestamp(filetime.st_mtime)
        # Checks that the time difference is less than 1 second.
        self.assertLess(time_diff.microseconds, 1e6)
        # Check that the files weren't created in the past.
        self.assertGreaterEqual(time_diff.microseconds, 0)

    def test_flight_data(self):
        # Tests the flight data code.
        frame_list = flight_log_code.flight_data(
            self.flight_data_file_path,
            self.flight_data_file_name)
        # Checks that the expected frame dimensions are the correct size.
        frame_dimensions = [17780, 95220, 22860, 25400, 57141, 44436, 57132,
                            19044, 5, 3]
        if len(frame_list) == 10:
            for frame in range(len(frame_list)):
                self.assertEqual(frame_list[frame].size,
                                 frame_dimensions[frame])
        else:
            # Raises a fault if the length of the frame_list is not as
            # expected.
            raise ValueError('Frame list length is not as expected: {0} != 10'
                             .format(len(frame_list)))

    def test_checklist_finder(self):
        # Loads a checklist
        try:
            frame_list = flight_log_code.flight_data(self.checklist_file_path,
                                                     'Checklists_nominal.xlsx')
            # Filters the checklist for the correct data
            filtered_frame = \
                flight_log_code.checklist_finder(frame_list,
                                                 self.flight_number[0],
                                                 self.flight_date[0])
            # Check that the correct data was output
            battery_voltage = filtered_frame['Battery Voltages'][2]
            self.assertEqual('25.2', str(battery_voltage))
            # Check that the ID also matches
            id_chosen_frame = filtered_frame['ID'][2]
            self.assertEqual('3', str(id_chosen_frame))
        # Passes if the checklist is open.
        except PermissionError:
            self.assertEqual(1, 1)

    def test_flight_log_creator(self):
        # Generates content
        content = flight_log_code.contents_opener(self.template_file_path,
                                                  self.template_file_name)
        file_name_data = str(self.flight_date[0]) + "_" + str(self.flight_number[0])
        # Runs the flight log creator code
        flight_log_code.flight_log_creator(content, self.base_path,
                                           file_name_data,
                                           self.flight_log_file_name_header)
        # Checks the file was created correctly
        file_exists = os.path.exists(self.base_path
                                     + 'test_generated_flight_log20190123'
                                       '_2.ipynb')
        self.assertTrue(file_exists)

    def test_flight_log_checklist(self):
        # Generates the content
        content = flight_log_code.contents_opener(self.template_file_path,
                                                  self.template_file_name)
        # Creates checklist frames
        frame_list_nominal = flight_log_code.flight_data(
            self.checklist_file_path, "Checklists_nominal.xlsx")
        frame_list_emergency = flight_log_code.flight_data(
            self.checklist_file_path, "Checklists_emergency.xlsx")
        # Filters checklist for the current flight
        filtered_frame_nominal = flight_log_code.checklist_finder(
            frame_list_nominal, self.flight_number[0], self.flight_date[0])
        filtered_frame_emergency = flight_log_code.checklist_finder(
            frame_list_emergency, self.flight_number[0], self.flight_date[0])
        # Runs the flight_log_checklist code
        content = \
            flight_log_code.flight_log_checklist(filtered_frame_nominal,
                                                 filtered_frame_emergency,
                                                 "CHECKLIST_INFORMATION",
                                                 content)[0]
        # Checks that the content has been changed
        expected_content = 'The Initial Pre-Flight was actioned by Adria' + \
                           'n Weishaeupl starting at 2019-01-23 15:31:44 an' + \
                           'd ending at 2019-01-23 15:32:58. The notes reco' + \
                           'rded on this checklist were: <i>THIS IS A TEST.'
        content_present = check_str_in_content(expected_content, content)
        self.assertEqual(1, content_present)

    def test_date_and_flight_number(self):
        # Gets run in the Jupyter Notebook.
        # Extracts the desired variables from the sample notebook
        date_and_flight_number = notebook_results[1]
        # Checks that the output is as expected
        expected_date_and_flight_number = ('20190123', '2')
        self.assertEqual(expected_date_and_flight_number,
                         date_and_flight_number)

    def test_arduino_micro_frame(self):
        # Gets run in the Jupyter Notebook.
        # Runs the sample notebook code to extract teh desired variable
        arduino_micro_frame = notebook_results[2]
        try:
            # Checks if the key is correct
            arduino_micro_frame['X']
            # Failed if no error is raised
            self.assertFalse(True)
        except KeyError:
            # Passes if an error is raised
            self.assertTrue(True)
        # Loads values
        values = arduino_micro_frame['Temp0_degC_ArduinoMicro_20190123_Flight2'
        ]
        # Compares expected values with values from the data frame
        expected_values = [24.38, 24.38, 24.38, 24.44, 25.31, 26.69, 27.69,
                           28.44, 29.00, 29.38, 29.69, 30.00, 30.06, 29.69,
                           29.38, 29.06, 28.81, 28.63, 28.38, 28.25, 28.06,
                           27.88, 27.75, 27.63, 27.50, 27.38, 27.25]
        for item in range(len(expected_values)):
            self.assertEqual(expected_values[item], values[item])

    def test_flight_data_time_sorter(self):
        # Gets run in the Jupyter Notebook.
        data_frames = notebook_results[3]
        # Checks that the frames were split into the correct number of
        # subframes
        self.assertEqual(len(data_frames), 10)
        # Assigns expected titles
        data_frame_section_titles = [
            'Status_unavailable_GPS_20190123_Flight2',
            'aileron_CH1_us_RCIN_20190123_Flight2',
            'Altitude_m_BARO_20190123_Flight2',
            'Airspeed_mpers_ARSP_20190123_Flight2',
            'Desired_Roll_degrees_ATT_20190123_Flight2',
            'VibeX_mperspers_VIBE_20190123_Flight2',
            'NavRoll_unavailable_CTUN_20190123_Flight2',
            'AOA_degrees_AOA_20190123_Flight2',
            'Action_time_hh:mm',
            'Temp0_degC_ArduinoMicro_20190123_Flight2']
        correct_titles = 0
        # Runs through titles. Checks that each title can be called and adds 1
        # to the counter (correct_titles). If a title is not correct/cannot be
        # called, raise a failure.
        for item in range(len(data_frame_section_titles)):
            try:
                data_frames[item][data_frame_section_titles[item]]
                correct_titles += 1
            except KeyError:
                self.assertEqual(1, 2)
        # Checks that all titles are correct
        self.assertEqual(correct_titles, 10)

    def test_flight_data_and_axis(self):
        # Gets run in the Jupyter Notebook.
        # Loads the data generated previously
        flight_data_and_axis = notebook_results[4]
        # Assigns expected titles
        expected_titles = ['GPS', 'RCIN', 'BARO', 'ARSP', 'ATT', 'VIBE',
                           'CTUN', 'AOA', 'Action', 'ArduinoMicro']
        # Checks that the titles are present and in the correct palace
        for item in range(len(expected_titles)):
            self.assertEqual(expected_titles[item], flight_data_and_axis[1][item][0])

    def test_file_type_finder(self):
        # Detects xlsx files from the test_files folder
        detected_files = flight_log_code.file_type_finder(self.base_path, ".xlsx")
        expected_file_names = ['Checklists_emergency.xlsx', 'Checklists_nominal.xlsx', 'test_xlsx.xlsx']
        # Checks that all the expected files are present
        for file_name in expected_file_names:
            if file_name in detected_files:
                file_detected = True
            else:
                file_detected = False
            self.assertTrue(file_detected)

    def test_compile_and_compress(self):
        # Runs the compiler and compressor.
        flight_log_code.compile_and_compress(self.flight_data_file_path, [self.flight_data_file_name],
                                             self.arduino_flight_data_file_path, self.arduino_flight_data_name,
                                             self.comp_data_file_path)
        pickle_file_name = self.base_path + "test_xlsx.pkl"  # Defines the file name
        # Checks that the file exists
        self.assertTrue(os.path.exists(pickle_file_name))

    def test_dictionary_reader(self):
        # Returns a string of formatted weather data
        read_data = flight_log_code.dictionary_reader(self.weather_data_dict, units_present=True)
        # Adds a string of formatted runway data
        read_data += flight_log_code.dictionary_reader(self.runway_data_dict, units_present=False)
        expected_results = ["Action time : 12:34 hh:mm", "Pressure : 1234567 Pa", "Temperature : -12.3 C",
                            "Wind direction : 123 degrees", "Wind speed : 12.3 mps", "take off direction : 321",
                            "runway surface : XYZ", "surface condition : ZYX"]
        # Checks that the correct data is present in the read_data string
        for string in expected_results:
            self.assertTrue(string in read_data)

    def test_multi_string_data_formatter(self):
        """A method to test the multi_string_data_formatter()"""
        # Assigns testing strings
        input1 = "Fish,Ca t,Dog,35, Mouse,   89"
        flight_names_1 = [1, 2, 3, 4, 5, 6]
        debug_name_1 = "Input 1"
        input2 = ""
        flight_names_2 = [0, 1]
        debug_name_2 = "Input 2"
        input3 = "Fail1"
        flight_names_3 = [7, 8]
        debug_name_3 = "TEST"
        # Assigns testing outputs
        expected_output1 = ["Fish", "Cat", "Dog", "35", "Mouse", "89"]
        expected_output2 = [""]
        expected_output3 = False
        # Tests that the method works as expected
        self.assertEqual(flight_log_code.multi_string_data_formatter(input1, flight_names_1, debug_name_1),
                         expected_output1)
        self.assertEqual(flight_log_code.multi_string_data_formatter(input2, flight_names_2, debug_name_2),
                         expected_output2)
        try:
            flight_log_code.multi_string_data_formatter(input3, flight_names_3, debug_name_3)
            # Should raise an index error. If not, fail the test.
            self.assertTrue(expected_output3)
        except IndexError:
            # Planned error
            self.assertTrue(True)

    def test_remove_dictionary_key(self):
        """A method to test the remove_dictionary_key()"""
        # Create variables
        dictionary1 = {"DOG": "4F", "Mouse": "Cat", "Donkey": 7, 8906: "Fish", "PiG": "Farm"}
        keys_to_remove = ["Mouse", 8906, "DOG"]
        # Remove the keys and check if they have been removed
        for key_index in range(len(keys_to_remove)):
            output = flight_log_code.remove_dictionary_key(dictionary1, keys_to_remove[key_index])
            if keys_to_remove[key_index] in output.keys():
                # Fail if the key is still present
                self.assertTrue(False)
            else:
                # Key successfully removed, pass the test
                self.assertTrue(True)

    def test_multi_dictionary_data_formatter(self):
        """A method to test the multi_dictionary_data_formatter()"""
        # Create variables
        dictionary1 = {"DOG": "4F, Squirrel", "Mouse": "Cat, 78", "Donkey": "7, 7", 8906: "Fish , Bird",
                       "PiG": "Farm, Animal"}
        debug_name1 = "dict1"
        flight_dates1 = [0, 1]
        dictionary2 = {"Face": "Nose, Ear, Mouth"}
        flight_dates2 = [2, 3]
        debug_name2 = "TEST"

        # Assigns expected outputs:
        expected_output_dict1_1 = ["4F", "Cat", "7", "Fish", "Farm"]
        expected_output_dict1_2 = ["Squirrel", "78", "7", "Bird", "Animal"]
        key = ["DOG", "Mouse", "Donkey", 8906, "PiG"]
        expected_output_dict2 = False

        # Runs the method
        output1 = flight_log_code.multi_dictionary_data_formatter(dictionary1, flight_dates1, debug_name1)

        try:
            flight_log_code.multi_dictionary_data_formatter(dictionary2, flight_dates2, debug_name2)
            # Fails if this does not raise an error
            self.assertTrue(expected_output_dict2)
        except IndexError:
            # Passes if an error is raised
            self.assertFalse(expected_output_dict2)

        for key_index in range(len(dictionary1.keys())):
            self.assertEqual(output1[0][key[key_index]], expected_output_dict1_1[key_index])
            self.assertEqual(output1[1][key[key_index]], expected_output_dict1_2[key_index])


if __name__ == '__main__':
    unittest.main()
