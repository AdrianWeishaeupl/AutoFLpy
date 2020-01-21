# -*- coding: utf-8 -*-
"""
Unit tests for the flight_log_code.py and the log_to_xlsx.py
codes. *** WORK IN PROGRESS ***
No tests are currently written for the GUI.

@author Adrian Weishaeupl (aw6g15@soton.ac.uk)
"""

import unittest
import os
import json
import sys
from autoflpy.util import flight_log_code
from datetime import datetime
from autoflpy.util import nearest_ICAO_finder
from shutil import copyfile


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
    # Excell Sheets
    frame_list = flight_log_code.flight_data(flight_data_file_path,
                                             flight_data_file_name)
    # A list containing the date first and then the flight number
    Date_and_flight_Number = flight_log_code.date_and_flight_number(frame_list)
    # Retrieves arduino flight data
    arduino_micro_flight_data_frame =\
        flight_log_code.arduino_micro_frame(arduino_data_file_path,
                                            arduino_flight_data_name)
    # Appends audino frame to flight data from pixhawk
    frame_list.append(arduino_micro_flight_data_frame)
    # Sorts frames by time
    sorted_frames = flight_log_code.flight_data_time_sorter(frame_list)
    # Creates a list of all the values.
    values_list = flight_log_code.flight_data_and_axis(sorted_frames)
    return(frame_list, Date_and_flight_Number, arduino_micro_flight_data_frame,
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
        # Populates the clobal variable
        notebook_results =\
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
        self.flight_number = self.data["log_to_xlsx_input"]["flight_number"]
        self.flight_date = self.data["log_to_xlsx_input"]["date"]
        self.template_file_path = self.base_path
        self.template_file_name = self.data["flight_log_generator_input"][
                "template_file_name"]
        self.flight_log_file_path = self.base_path + self.data[
                "flight_log_generator_input"]["flight_log_destination"]
        self.flight_data_file_path = self.base_path  # Path to xlsx file
        self.flight_data_file_name = "test_xlsx.xlsx"
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
            "test_generated_flight_log20190123_2.ipynb"
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
            'test_generated_flight_log20190123_2.ipynb'
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
        frame_dimensions = [17780, 95220, 22860, 25400, 57141, 44436, 57132,
                            19044]
        if len(frame_list) == 8:
            for frame in range(len(frame_list)):
                self.assertEqual(frame_list[frame].size,
                                 frame_dimensions[frame])
        else:
            # Raises a fault if the length of the frame_list is not as
            # expected.
            raise ValueError('Frame list length is not as expected: {0} != 8'
                             .format(len(frame_list)))

    def test_checklist_finder(self):
        # Loads a checklist
        try:
            frame_list = flight_log_code.flight_data(self.checklist_file_path,
                                                     'Checklists_nominal.xlsx')
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
        test_string_true = 'o view images, place the images in a folder' +\
            ' called images (a'
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
        check_graph_plotter = check_str_in_content('graph_plotter', contents)
        self.assertEqual(26, check_x_lim)
        self.assertEqual(26, check_y_lim)
        self.assertEqual(13, check_graph_plotter)

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
        check_graph_plotter = check_str_in_content('graph_plotter', contents)
        self.assertEqual(6, check_x_lim)
        self.assertEqual(12, check_y_lim)  # Note: multiple y axis inputs.
        self.assertEqual(3, check_graph_plotter)

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
                                     '_2.ipynb')
        self.assertTrue(file_exists)

    def test_METAR_finder(self):
        # Checks if the METAR data exists. If it doesn't, it gets it from the
        # API. NOTE: API has a limit and so the original METAR file is not
        # deleted before every run.
        flight_log_code.metar_finder('EGHE', '2019', '01', '23', '01', '23',
                                     '9', '10', self.base_path)
        # Checks if the file path exists.
        metar_data_exists = os.path.exists(self.base_path + 'METAR_EGHE_2019'
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
        metar_data = flight_log_code.metar_finder('EGHE', '2019', '01', '23',
                                                  '01', '23', '9', '10',
                                                  self.base_path)
        # Runs METAR returner
        content = flight_log_code.metar_returner(metar_data, content, 1,
                                                 2019,
                                                 replace_key="METAR_"
                                                 "INFORMATION")
        # Assigns expected metar information
        metar_information = "type: routine report, cycle 9 (automatic report)"
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
        content = flight_log_code.no_metar_returner('EGHE', '2019', '01', '23',
                                                    '01', '23', '9', '10',
                                                    content, replace_key="META"
                                                    "R_INFORMATION")
        # Assigns expected content
        expected_content = 'No METARs for EGHE for the date 23012019 to the date 23012019 from a '\
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
        content = flight_log_code.metar_quota_returner(content, 'test20190123',
                                                       'EGHE', '2019', '01',
                                                       '23', '01', '23', '9',
                                                       '10', self.base_path,
                                                       replace_key="METAR_INFO"
                                                       "RMATION")
        expected_content = 'metar_replacer(os.getcwd(),'
        content_present = check_str_in_content(expected_content, content)
        self.assertEqual(1, content_present)

    def test_METAR_replacer(self):
        # Creates a backup copy to work on
        template_temp_name = self.template_file_name[:-6] + '_temp.ipynb'
        copyfile(self.template_file_path + self.template_file_name,
                 self.template_file_path + template_temp_name)
        # Generates content
        content = flight_log_code.contents_opener(self.template_file_path,
                                                  template_temp_name)
        # Check that # METAR REPLACER is present in the content
        metar_information_present = check_str_in_content("# METAR REPLACER",
                                                         content)
        self.assertEqual(1, metar_information_present)
        # Run the METAR_replacer
        content = flight_log_code.metar_replacer(self.template_file_path,
                                                 template_temp_name,
                                                 'EGHE', '2019', '01', '23',
                                                 '01', '23', '9', '10',
                                                 self.base_path)
        # Check information was replaced correctly
        # Re-reads content
        content = flight_log_code.contents_opener(self.template_file_path,
                                                  template_temp_name)
        # Checks that the METAR data is present
        expected_content = 'time: Wed Jan 23 09'
        metar_in_content = check_str_in_content(expected_content, content)
        # NOTE: also replaces the content of the METAR_INFORMATION cell, hence
        # 2 instances are present in this test. This is also only relevant to
        # the test template.
        self.assertEqual(4, metar_in_content)
        # Removes the generated document
        generated_file_name = self.template_file_path + template_temp_name
        if os.path.exists(generated_file_name):
            os.remove(generated_file_name)

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
                frame_list_nominal, self.flight_number, self.flight_date)
        filtered_frame_emergency = flight_log_code.checklist_finder(
                frame_list_emergency, self.flight_number, self.flight_date)
        # Runs the flight_log_checklist code
        content = \
            flight_log_code.flight_log_checklist(filtered_frame_nominal,
                                                 filtered_frame_emergency,
                                                 "CHECKLIST_INFORMATION",
                                                 content)[0]
        # Checks that the content has been changed
        expected_content = 'The Initial Pre-Flight was actioned by Adria' +\
                           'n Weishaeupl starting at 2019-01-23 15:31:44 an' +\
                           'd ending at 2019-01-23 15:32:58. The notes reco' +\
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
        self.assertEqual(len(data_frames), 9)
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
        self.assertEqual(correct_titles, 9)
        pass  # Not yet written.

    def test_flight_data_and_axis(self):
        # Gets run in the Jupyter Notebook.
        # Loads the data generated previously
        flight_data_and_axis = notebook_results[4]
        # Assigns expected titles
        expected_titles = ['GPS', 'RCIN', 'BARO', 'ARSP', 'ATT', 'VIBE',
                           'CTUN', 'AOA', 'ArduinoMicro']
        # Checks that the titles are present and in the correct palace
        for item in range(len(expected_titles)):
            self.assertEqual(flight_data_and_axis[item][0],
                             expected_titles[item])

    def test_file_type_finder(self):
        pass  # Not yet written.


if __name__ == '__main__':
    unittest.main()
