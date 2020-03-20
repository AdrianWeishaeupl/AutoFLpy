# -*- coding: utf-8 -*-
"""
Unit tests for the name_generator function
Created on Thu Nov 21 14:53:20 2019

@author Adrian Weishaeupl (aw6g15@soton.ac.uk)
"""

from autoflpy.util import name_generator
import unittest


class TestNameGenerator(unittest.TestCase):

    def setUp(self):
        # Defines variables needed
        self.date = [12345678]
        self.flight_number = [2]

    def test_name_generator(self):
        # Runs the name generator code
        name_generator.excel_file_name_updater(self.date, self.flight_number)
        # Assigns expected outcome
        expected_name = '12345678_Flight02'
        # Checks that the expected outcome is as expected
        self.assertEqual(expected_name, name_generator.generated_file_name[0])


if __name__ == '__main__':
    unittest.main()
