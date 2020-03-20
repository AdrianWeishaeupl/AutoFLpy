# -*- coding: utf-8 -*-
"""
Unit tests for the metar_processing.py code.

@author Adrian Weishaeupl (aw6g15@soton.ac.uk)
"""

import unittest
import os
import json
from autoflpy.util import metar_processing
from shutil import copyfile
from datetime import datetime
from autoflpy.util.testing.check_str_in_content import *
from autoflpy.util.text_manipulation import contents_opener


class TestMetarProcessing(unittest.TestCase):

    def setUp(self):
        # Sets up all of the test variables and locations to be used
        # throughout.
        self.base_path = os.path.join(os.path.dirname(__file__), "test_files") + os.sep
        self.base_path = self.base_path.replace(os.sep, "/")
        # Imports data from template.
        with open(self.base_path + 'test_Input_File.json') as file:
            self.data = json.load(file)
        self.template_file_path = self.base_path
        self.template_file_name = self.data["flight_log_generator_input"]["template_file_name"]

        copyfile(self.base_path + "test_generated_flight_logtest_metar.ipynb",
                 self.base_path + "metar_testing.ipynb")

    def tearDown(self):
        if os.path.exists(self.base_path + "metar_testing.ipynb"):
            os.remove(self.base_path + "metar_testing.ipynb")
        pass

    def test_METAR_finder(self):
        # Checks if the METAR data exists. If it doesn't, it gets it from the
        # API. NOTE: API has a limit and so the original METAR file is not
        # deleted before every run.
        metar_processing.metar_finder('EGHE', '2019', '01', '23', '01', '23',
                                      '9', '10', self.base_path)
        # Checks if the file path exists.
        metar_data_exists = os.path.exists(self.base_path + 'METAR_EGHE_2019'
                                           '0123_20190123_9_9.txt')
        self.assertTrue(metar_data_exists)

    def test_METAR_returner(self):
        # Generate content
        content = metar_processing.contents_opener(self.template_file_path,
                                                   self.template_file_name)

        # Check that METAR_INFORMATION is present in the content
        metar_information_present = check_str_in_content("METAR_INFORMATION",
                                                         content)
        self.assertEqual(1, metar_information_present)
        # Gets METAR data
        metar_data = metar_processing.metar_finder('EGHE', '2019', '01', '23',
                                                   '01', '23', '9', '10',
                                                   self.base_path)
        # Runs METAR returner
        content = metar_processing.metar_returner(metar_data, content, [1],
                                                  [2019], 1,
                                                  replace_key="METAR_"
                                                  "INFORMATION")
        # Assigns expected metar information
        metar_information = "type: routine report, cycle 9 (automatic report)"
        # Checks that the expected metar information is present
        metar_information_present = check_str_in_content(metar_information,
                                                         content)
        self.assertEqual(1, metar_information_present)

    def test_no_METAR_returner(self):
        content = metar_processing.contents_opener(self.template_file_path,
                                                   self.template_file_name)

        # Check that METAR_INFORMATION is present in the content
        metar_information_present = check_str_in_content("METAR_INFORMATION",
                                                         content)
        self.assertEqual(1, metar_information_present)
        # Runs no_METAR_returner code
        content = metar_processing.no_metar_returner(['EGHE'], [20190123], [20190123], ['9'], ['10'],
                                                     content, 1, replace_key="META"
                                                     "R_INFORMATION")
        # Assigns expected content
        expected_content = 'No METARs for EGHE for the date 23/01/2019 to the date 23/01/2019 from a starting time of' \
                           ' 9:00 and an end time of 9:59.'
        # Checks that the expected content is present in the content
        information_present = check_str_in_content(expected_content,
                                                   content)
        self.assertEqual(1, information_present)

    def test_METAR_quota_returner(self):
        content = metar_processing.contents_opener(self.template_file_path,
                                                   self.template_file_name)

        # Check that METAR_INFORMATION is present in the content
        metar_information_present = check_str_in_content("METAR_INFORMATION",
                                                         content)
        self.assertEqual(1, metar_information_present)
        # Runs METAR_quota_returner
        content = metar_processing.metar_quota_returner(content, 'test20190123',
                                                        ['EGHE'], ['2019'], ['01'],
                                                        ['23'], ['01'], ['23'], ['9'],
                                                        ['10'], self.base_path, 1,
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
        content = metar_processing.contents_opener(self.template_file_path,
                                                   template_temp_name)
        # Check that # METAR REPLACER is present in the content
        metar_information_present = check_str_in_content("# METAR REPLACER",
                                                         content)
        self.assertEqual(1, metar_information_present)
        # Run the METAR_replacer
        metar_processing.metar_replacer(self.template_file_path,
                                        template_temp_name,
                                        'EGHE', '2019', '01', '23',
                                        '01', '23', '9', '10', 0,
                                        self.base_path)
        # Check information was replaced correctly
        # Re-reads content
        content = metar_processing.contents_opener(self.template_file_path,
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

    def test_metar_replacer(self):
        """Tests the metar_replacer()
        TODO: This test needs to be more thorough
        """
        file_path = self.base_path
        file_name = "metar_testing.ipynb"
        location = "EGHE_20190123_20190123_9_9"
        year = "2019"
        month = "01"
        day = "23"
        month_end = "01"
        day_end = "23"
        start_time_hours = "9"
        end_time_hours = "10"
        flight = 0
        metar_file_path = self.base_path

        metar_processing.metar_replacer(file_path, file_name, location, year, month, day,
                                        month_end, day_end, start_time_hours, end_time_hours, flight,
                                        metar_file_path)

        # Checks that the file was recently created.
        filetime = os.stat(file_path + file_name)
        # Finds the time since the file has been created.
        time_diff = datetime.now() - datetime.fromtimestamp(filetime.st_mtime)
        # Checks that the time difference is less than 0.5 seconds.
        self.assertLess(time_diff.microseconds, 5e5)
        # Check that the files weren't created in the past.
        self.assertGreaterEqual(time_diff.microseconds, 0)


if __name__ == '__main__':
    unittest.main()
