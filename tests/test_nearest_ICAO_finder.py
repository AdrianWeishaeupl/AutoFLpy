# -*- coding: utf-8 -*-
"""
Unittests for the nearest_ICAO_finder code.

@author: Adrian Weishaeupl
aw6g15@soton.ac.uk 2019
"""

from autoflpy.util import nearest_ICAO_finder
import unittest


class Testnearest_ICAO_finder(unittest.TestCase):

    def setUp(self):
        # Defines variables needed
        pass

    def test_icao_finder(self):
        # To be written
        pass

    def test_closest_icao(self):
        # To be written
        pass

    def test_airport_lat_long(self):
        # Runs the airport_lat_long function
        airport_lat_long = nearest_ICAO_finder.airport_lat_long()
        # Creates lists of items and expected results
        item_check = [10, 100, 1000, 10000, 20000, 30000, 40488]
        expected_ICAOs = ['00FL', '01OI', '0PA1', '9MI6', 'KDGL', 'RJNO',
                          'ZZZZ']
        for item_index in range(len(item_check)):
            # Finds ICAO
            icao = airport_lat_long[item_check[item_index]][0]
            # Compares ICAO to the expected index
            expected_ICAO = expected_ICAOs[item_index]
            self.assertEqual(icao, expected_ICAO)

    def test_uav_lat_long(self):
        # To be written
        pass


if __name__ == '__main__':
    unittest.main()
