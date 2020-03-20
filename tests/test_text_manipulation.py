# -*- coding: utf-8 -*-
"""
Unit tests for the text manipulation function
Created on Tue Feb 18 14:53:20 2020

@author Adrian Weishaeupl (aw6g15@soton.ac.uk)
"""

import unittest
import os
import json
from autoflpy.util import text_manipulation
from autoflpy.util.testing.check_str_in_content import *


class TestTextManipulation(unittest.TestCase):

    def setUp(self):
        # Sets up all of the test variables and locations to be used
        # throughout.
        self.base_path = os.path.join(os.path.dirname(__file__),
                                      "test_files") + os.sep
        self.base_path = self.base_path.replace(os.sep, "/")
        # Imports data from template.
        with open(self.base_path + 'test_Input_File.json') as file:
            self.data = json.load(file)
        self.template_file_path = self.base_path
        self.template_file_name = self.data["flight_log_generator_input"][
                "template_file_name"]

    def test_contents_opener(self):
        contents = text_manipulation.contents_opener(self.template_file_path,
                                                     self.template_file_name)
        test_string = (contents[370:430])
        test_string_true = 'o view images, place the images in a folder' +\
            ' called images (a'
        self.assertEqual(test_string_true, test_string)

    def test_flight_log_graph_contents_replacer(self):
        # Function being tested is expected to replace all fields with
        # single axis graphs.
        # Generates content.
        contents = text_manipulation.contents_opener(self.template_file_path,
                                                     self.template_file_name)
        # Runs the flight_log_content_replacer
        contents = text_manipulation.flight_log_graph_contents_replacer(contents)
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
        contents = text_manipulation.contents_opener(self.template_file_path,
                                                     self.template_file_name)
        # Runs the flight_log_content_replacer
        contents = text_manipulation. \
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
            content = text_manipulation.contents_opener(self.template_file_path,
                                                        self.template_file_name)
            # Counts the keys in the content
            content_count = check_str_in_content(key, content)
            # Checks that the keys are present
            self.assertNotEqual(0, content_count)
            # Runs cell remover
            content = text_manipulation.cell_remover(content, key)
            # Counts Key occurrences
            content_count = check_str_in_content(key, content)
            # Checks that the cell has been removed
            self.assertEqual(0, content_count)

    def test_line_remover(self):
        # Defines keys to be tested in the line remover
        keys = ['METAR_INFORMATION', 'CHECKLIST_INFORMATION', 'GRAPH',
                'MULTIAXIS_GRAPH', 'CHECKLIST_LINE', 'GRAPH_LINE']
        for key in keys:
            # Generates content
            content = text_manipulation.contents_opener(self.template_file_path,
                                                        self.template_file_name)
            # Counts how many times the key is present
            content_count = check_str_in_content(key, content)
            # Checks that the key is present
            self.assertNotEqual(0, content_count)
            # Runs line remover
            content = text_manipulation.line_remover(content, key)
            # Counts Key occurrences
            content_count = check_str_in_content(key, content)
            # Checks that the line has been removed
            self.assertEqual(0, content_count)

    def test_contents_opener(self):
        """Tests the contents_opener()"""
        # Assigns variables
        file_path = self.base_path
        file_name1 = "test_data_sources.txt"
        file_name2 = "METAR_EGHE_20190123_20190123_9_9.txt"

        # Assigns outputs
        expected_output1 = "Data Sources specified here will be placed in the excel document\nGPS\nAOA\nCTUN\n" \
                           "RCIN\nARSP\nBARO\nATT\nVIBE"
        expected_output2 = "METAR EGHE 230950Z 34017KT 9999 SCT025 08/03 Q1007\nMETAR EGHE 230920Z 34017KT 9999" \
                           " SCT022 08/02 Q1006\nhttps://www.ogimet.com/display_metars2.php?lang=en&lugar=EGHE&t" \
                           "ipo=ALL&ord=REV&nil=SI&fmt=html&ano=2019&mes=01&day=23&hora=9&anof=2019&mesf=01&dayf=" \
                           "23&horaf=9&minf=59&send=send"

        # Runs method
        output1 = text_manipulation.contents_opener(file_path, file_name1)
        output2 = text_manipulation.contents_opener(file_path, file_name2)

        # Checks results match
        self.assertEqual(output1, expected_output1)
        self.assertEqual(output2, expected_output2)


if __name__ == '__main__':
    unittest.main()
