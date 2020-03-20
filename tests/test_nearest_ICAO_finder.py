# -*- coding: utf-8 -*-
"""
Unittests for the nearest_ICAO_finder code.

@author: Adrian Weishaeupl
aw6g15@soton.ac.uk 2019
"""

from autoflpy.util import nearest_ICAO_finder
import unittest
import numpy as np
import os


class TestNearestICAOFinder(unittest.TestCase):

    def setUp(self):
        # Defines variables needed
        # Set the working directory
        base_path = os.path.join(os.path.dirname(__file__),
                                 "test_files") + os.sep
        # Tidies up the base path for python.
        self.base_path = base_path.replace(os.sep, "/")
        # Define the variables
        self.excel_file_path = self.base_path
        self.excel_file_name = "test_xlsx.xlsx"

    def test_icao_finder(self):
        # Runs icao_finder function
        icao = nearest_ICAO_finder.icao_finder(self.excel_file_path,
                                               self.excel_file_name)
        # Checks that the correct icao code is returned.
        self.assertEqual('EGHE', icao)

    def test_closest_icao(self):
        # Runs the airport_lat_long_clst function
        airport_lat_long = nearest_ICAO_finder.airport_lat_long()
        # Arbitrary latitude and longitude for checking
        uav_lat_long_check = [[[51.067397], [-1.320574]],
                              [[50.154234], [8.735601]],
                              [[49.721109], [-102.279640]],
                              [[-40.424322], [-68.260537]],
                              [[-8.266594], [28.914712]]]
        # Defines the expected outputs
        expected_closest_icao = [14637, 14122, 12234, 30551, 16258]
        # Runs closest_icao function from the nearest_ICAO_finder.py
        for lat_long in range(len(uav_lat_long_check)):
            result = nearest_ICAO_finder.closest_icao(np.array(
                    uav_lat_long_check[lat_long]), np.array(
                            [airport_lat_long[:, 1], airport_lat_long[:, 2]]))
            # Check the results are equal to the expected
            self.assertEqual(result, expected_closest_icao[lat_long])

    def test_airport_lat_long(self):
        # Runs the airport_lat_long_clst function
        airport_lat_long = nearest_ICAO_finder.airport_lat_long()
        # Creates lists of items and expected results
        item_check = [10, 100, 1000, 10000, 20000, 30000, 40488]
        expected_icaos = ['00FL', '01OI', '0PA1', '9MI6', 'KDGL', 'RJNO',
                          'ZZZZ']
        for item_index in range(len(item_check)):
            # Finds ICAO
            icao = airport_lat_long[item_check[item_index]][0]
            # Compares ICAO to the expected index
            expected_icao = expected_icaos[item_index]
            self.assertEqual(icao, expected_icao)

    def test_uav_lat_long(self):
        # Runs the uav_lat_long_clst function from the nearest_ICAO_finder.py
        uav_lat_long = nearest_ICAO_finder.uav_lat_long(self.excel_file_path,
                                                        self.excel_file_name)
        # Defines expected_results
        expected_lat_long = np.array([[49.9543952], [-6.3688301]])
        # Compares the uav_lat_long_clst to the expected_lat_long, 0 = lat, 1 = long
        self.assertEqual(expected_lat_long[0], uav_lat_long[0])
        self.assertEqual(expected_lat_long[1], uav_lat_long[1])

    def test_multi_icao_finder(self):
        """Tests the multi_icao_finder()"""
        # Assigns variables
        file_path = self.base_path
        file_names = [self.excel_file_name, self.excel_file_name]
        flight_names = ["test_xlsx.xlsx", "test_xlsx.xlsx"]

        # Runs the method
        icaos = nearest_ICAO_finder.multi_icao_finder(file_path, file_names, flight_names)

        # Tests the results
        expected_icaos = ["EGHE", "EGHE"]
        for item in range(len(icaos)):
            self.assertEqual(icaos[item], expected_icaos[item])


if __name__ == '__main__':
    unittest.main()
