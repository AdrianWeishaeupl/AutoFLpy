# -*- coding: utf-8 -*-
"""
Unit tests for the flight_log_code.py and the log_to_xls.py
codes. *** WORK IN PROGRESS ***
No tests are currently written for the GUI.

@author Adrian Weishaeupl (aw6g15@soton.ac.uk)
"""

import unittest
import os
import json
from autoflpy.util import flight_log_code
from datetime import datetime
from autoflpy.util import nearest_ICAO_finder


def check_str_in_content(string, content):
    """Checks that a certain string is present in the content
    provided. This is case sensitive. This is used in the test functions."""
    if string in content:
        # Checks that the string is present in the content
        occurence = 0
        # Counts the number of occurences
        for section in range((len(content) - len(string) + 1)):
            if content[section:section + len(string)] == string:
                occurence = occurence + 1
            else:
                continue
    else:
        occurence = 0
    # Returns results
    return (occurence)


class Test_flight_log_code(unittest.TestCase):

    def setUp(self):
        # Sets up all of the test variables and locations to be used
        # throughout.
        self.base_path = os.path.join(os.path.dirname(__file__),
                                      "test_files") + os.sep
        self.base_path = self.base_path.replace(os.sep, "/")
        # Imports data from template.
        with open(self.base_path + 'test_Input File.json') as file:
            self.data = json.load(file)
        self.flight_number = self.data["log_to_xls_input"]["flight_number"]
        self.flight_date = self.data["log_to_xls_input"]["date"]
        self.template_file_path = self.base_path
        self.template_file_name = self.data["flight_log_generator_input"][
                "template_file_name"]
        self.flight_log_file_path = self.base_path + self.data[
                "flight_log_generator_input"]["flight_log_destination"]
        self.flight_data_file_path = self.base_path  # Path to xls file
        self.flight_data_file_name = "test_xls.xls"
        self.arduino_flight_data_file_path = self.base_path + self.data[
                "flight_log_generator_input"]["arduino_flight_data_file_path"]
        self.arduino_flight_data_name = self.data["flight_log_generator_input"
                                                  ]["arduino_flight_data_name"]
        self.flight_log_file_name_header = "test_generated_flight_log"
        self.checklist_file_path = self.base_path
        self.log_code_version = "autoflpy.flight_log_code"
        self.start_time_hours = self.data["flight_log_generator_input"][
                "start_time_hours"]
        self.end_time_hours = self.data["flight_log_generator_input"][
                "end_time_hours"]
        self.metar_file_path = self.base_path + self.data[
                "flight_log_generator_input"]["metar_file_path"]

    def tearDown(self):
        # Removes generated flight log.
        base_path = os.path.join(os.path.dirname(__file__),
                                 "test_files") + os.sep
        generated_file_name = base_path + \
            "test_generated_flight_log20190123 2.ipynb"
        if os.path.exists(generated_file_name):
            os.remove(generated_file_name)

    def test_flight_log_maker(self):
        self.ICAO_airfield = nearest_ICAO_finder.icao_finder(
                self.flight_data_file_path,
                self.flight_data_file_name)
        flight_log_code.flight_log_maker(self.template_file_path,
                                         self.template_file_name,
                                         self.flight_log_file_path,
                                         self.flight_data_file_path,
                                         self.flight_data_file_name,
                                         self.arduino_flight_data_file_path,
                                         self.arduino_flight_data_name,
                                         self.flight_date,
                                         self.flight_number,
                                         self.flight_log_file_name_header,
                                         self.checklist_file_path,
                                         self.log_code_version,
                                         self.ICAO_airfield,
                                         self.start_time_hours,
                                         self.end_time_hours,
                                         self.metar_file_path)
        # This code tests the flight_log_maker function.
        # First, check that a file has been created.
        test_flight_log_file_path = self.base_path + \
            'test_generated_flight_log20190123 2.ipynb'
        if os.path.exists(test_flight_log_file_path) is True:
            file_exists = True
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
        frame_dimensions = [17693, 102030, 21784, 24498, 61218, 47614, 61218,
                            20406]
        if len(frame_list) == 8:
            for frame in range(len(frame_list)):
                self.assertEqual(frame_list[frame].size,
                                 frame_dimensions[frame])
        else:
            # Raises a fault if the length of the frame_list is not as
            # expected.
            self.assertEqual(1, 2)

    def test_checklist_finder(self):
        # Loads a checklist
        try:
            frame_list = flight_log_code.flight_data(self.checklist_file_path,
                                                     'Checklists nominal.xlsx')
            # Filters the checklist for the correct data
            filtered_frame = \
                flight_log_code.checklist_finder(frame_list,
                                                 self.flight_number,
                                                 self.flight_date)
            # Check that the correct data was output
            battery_voltage = filtered_frame['Battery Voltages'][2]
            self.assertEqual('25.2', str(battery_voltage))
            # Check that the ID also matches
            id_chosen_frame = filtered_frame['ID'][2]
            self.assertEqual('3', str(id_chosen_frame))
        # Passes if the checklist is open.
        except PermissionError:
            self.assertEqual(1, 1)

    def test_contents_opener(self):
        contents = flight_log_code.contents_opener(self.template_file_path,
                                                   self.template_file_name)
        test_string = (contents[370:430])
        test_string_true = 'go, To view images, place the images in a' + \
                           ' folder called imag'
        self.assertEqual(test_string_true, test_string)

    def test_flight_log_graph_contents_replacer(self):
        # Function being tested is expected to replace all fields with
        # single axis graphs.
        # Generates content.
        contents = flight_log_code.contents_opener(self.template_file_path,
                                                   self.template_file_name)
        # Runs the flight_log_content_replacer
        contents = flight_log_code.flight_log_graph_contents_replacer(contents)
        # Checks for values replaced by the function
        check_x_lim = check_str_in_content('x_limits', contents)
        check_y_lim = check_str_in_content('y_limits', contents)
        check_graph_function = check_str_in_content('graph_function', contents)
        self.assertEqual(24, check_x_lim)
        self.assertEqual(24, check_y_lim)
        self.assertEqual(12, check_graph_function)

    def test_flight_log_multiaxis_graph_contents_replacer(self):
        # Function being tested is expected to replace all fields with
        # multi-axis graphs.
        # Generates content.
        contents = flight_log_code.contents_opener(self.template_file_path,
                                                   self.template_file_name)
        # Runs the flight_log_content_replacer
        contents = flight_log_code.\
            flight_log_multiaxis_graph_contents_replacer(contents)
        # Checks for values replaced by the function
        check_x_lim = check_str_in_content('x_limits', contents)
        check_y_lim = check_str_in_content('y_limits', contents)
        check_graph_function = check_str_in_content('graph_function', contents)
        self.assertEqual(6, check_x_lim)
        self.assertEqual(12, check_y_lim)  # Note: multiple y axis inputs.
        self.assertEqual(3, check_graph_function)

    def test_cell_remover(self):
        # Defines keys to be tested in the cell remover
        keys = ['METAR_INFORMATION', 'CHECKLIST_INFORMATION', 'GRAPH',
                'MULTIAXIS_GRAPH']
        for key in keys:
            # Generates content
            content = flight_log_code.contents_opener(self.template_file_path,
                                                      self.template_file_name)
            # Counts the keys in the content
            content_count = check_str_in_content(key, content)
            # Checks that the keys are present
            self.assertNotEqual(0, content_count)
            # Runs cell remover
            content = flight_log_code.cell_remover(content, key)
            # Counts Key occurences
            content_count = check_str_in_content(key, content)
            # Checks that the cell has been removed
            self.assertEqual(0, content_count)

    def test_line_remover(self):
        # Defines keys to be tested in the line remover
        keys = ['METAR_INFORMATION', 'CHECKLIST_INFORMATION', 'GRAPH',
                'MULTIAXIS_GRAPH', 'CHECKLIST_LINE', 'GRAPH_LINE']
        for key in keys:
            # Generates content
            content = flight_log_code.contents_opener(self.template_file_path,
                                                      self.template_file_name)
            # Counts how many times the key is present
            content_count = check_str_in_content(key, content)
            # Checks that the key is present
            self.assertNotEqual(0, content_count)
            # Runs line remover
            content = flight_log_code.line_remover(content, key)
            # Counts Key occurences
            content_count = check_str_in_content(key, content)
            # Checks that the line has been removed
            self.assertEqual(0, content_count)

    def test_flight_log_creator(self):
        # Generates content
        content = flight_log_code.contents_opener(self.template_file_path,
                                                  self.template_file_name)
        # Runs the flight log creator code
        flight_log_code.flight_log_creator(content, self.base_path,
                                           self.flight_date,
                                           self.flight_number,
                                           self.flight_log_file_name_header)
        # Checks the file was created correctly
        file_exists = os.path.exists(self.base_path
                                     + 'test_generated_flight_log20190123'
                                     ' 2.ipynb')
        self.assertTrue(file_exists)

    def test_METAR_finder(self):
        # Checks if the METAR data exists. If it doesn't, it gets it from the
        # API. NOTE: API has a limit and so the original METAR file is not
        # deleted before every run.
        flight_log_code.METAR_finder('DGTK', '2019', '01', '23', '01', '23',
                                     '9', '10', self.base_path)
        # Checks if the file path exists.
        metar_data_exists = os.path.exists(self.base_path + 'METAR_DGTK_2019'
                                           '0123_20190123_9_9.txt')
        self.assertTrue(metar_data_exists)

    def test_METAR_returner(self):
        # Generate content
        content = flight_log_code.contents_opener(self.template_file_path,
                                                  self.template_file_name)

        # Check that METAR_INFORMATION is present in the content
        metar_information_present = check_str_in_content("METAR_INFORMATION",
                                                         content)
        self.assertEqual(1, metar_information_present)
        # Gets METAR data
        metar_data = flight_log_code.METAR_finder('DGTK', '2019', '01', '23',
                                                  '01', '23', '9', '10',
                                                  self.base_path)
        # Runs METAR returner
        content = flight_log_code.METAR_returner(metar_data, content, 1,
                                                 2019,
                                                 replace_key="METAR_"
                                                 "INFORMATION")
        # Assigns expected metar information
        metar_information = "METAR: DGTK 230900Z NIL"
        # Checks that the expected metar information is present
        metar_information_present = check_str_in_content(metar_information,
                                                         content)
        self.assertEqual(1, metar_information_present)

    def test_no_METAR_returner(self):
        content = flight_log_code.contents_opener(self.template_file_path,
                                                  self.template_file_name)

        # Check that METAR_INFORMATION is present in the content
        metar_information_present = check_str_in_content("METAR_INFORMATION",
                                                         content)
        self.assertEqual(1, metar_information_present)
        # Runs no_METAR_returner code
        content = flight_log_code.no_METAR_returner('DGTK', '2019', '01', '23',
                                                    '01', '23', '9', '10',
                                                    content, replace_key="META"
                                                    "R_INFORMATION")
        # Assigns expected content
        expected_content = 'No METARs for DGTK for the date 23012019 from a '\
            'starting time of 9:00 and an end time of 9:59.'
        # Checks that the expected content is present in the content
        information_present = check_str_in_content(expected_content,
                                                   content)
        self.assertEqual(1, information_present)

    def test_METAR_quota_returner(self):
        content = flight_log_code.contents_opener(self.template_file_path,
                                                  self.template_file_name)

        # Check that METAR_INFORMATION is present in the content
        metar_information_present = check_str_in_content("METAR_INFORMATION",
                                                         content)
        self.assertEqual(1, metar_information_present)
        # Runs METAR_quota_returner
        content = flight_log_code.METAR_quota_returner(content, 'test20190123',
                                                       'DGTK', '2019', '01',
                                                       '23', '01', '23', '9',
                                                       '10', self.base_path,
                                                       replace_key="METAR_INFO"
                                                       "RMATION")
        expected_content = 'METAR_replacer(os.getcwd(),'
        content_present = check_str_in_content(expected_content, content)
        self.assertEqual(1, content_present)

    def test_METAR_replacer(self):
        pass  # Not yet written.

    def test_arduino_micro_frame(self):
        pass  # Not yet written.

    def test_flight_log_checklist(self):
        pass  # Not yet written.

    def test_flight_data_and_axis(self):
        # Gets run in the Jupyter Notebook.
        pass  # Not yet written.

    def test_graph_function(self):
        # Gets run in the Jupyter Notebook.
        pass  # Not yet written.

    def test_multiaxis_graph_function(self):
        # Gets run in the Jupyter Notebook.
        pass  # Not yet written.

    def test_flight_data_time_sorter(self):
        # Gets run in the Jupyter Notebook.
        pass  # Not yet written.

    def test_file_type_finder(self):
        # Gets run in the Jupyter Notebook.
        pass  # Not yet written.

    def test_date_and_flight_number(self):
        # Gets run in the Jupyter Notebook.
        pass  # Not yet written.


if __name__ == '__main__':
    unittest.main()
