# -*- coding: utf-8 -*-
"""
Unit tests for the plotting.py code.
No tests are currently written for the main plotting methods.

@author Adrian Weishaeupl (aw6g15@soton.ac.uk)
"""

from autoflpy.util import plotting
import unittest
import os
import pickle as pk


class TestPlotting(unittest.TestCase):

    def setUp(self):
        # Create variables and assign directories before any test.
        base_path = os.path.join(os.path.dirname(__file__),
                                 "test_files") + os.sep
        # Tidies up the base path for python.
        self.base_path = base_path.replace(os.sep, "/")

        self.values_list = pk.load(open(base_path + "test_pickled_data.pkl", "rb"))

    def test_manual_time_offset(self):
        """Test for manual_time_offset()"""
        # Defining inputs
        time_x_offset = [1234]

        # Changes the values list to only include the data
        plot_data, flight_dates_list, single_flight, number_of_flights =\
            plotting.single_flight_detection(self.values_list)

        # Running the method
        values_list_offset = plotting.manual_time_offset(plot_data, time_x_offset, number_of_flights)

        # Loads "clean" values_list data - plotting.manual_time_offset() seems to add the offset to all time data
        # - no matter what variable it is in. Known to affect self.values_list, plot_data and values_list_offset
        values_list = pk.load(open(self.base_path + "test_pickled_data.pkl", "rb"))

        # Testing the result
        # time_data_gps = values_list[0][1][0][14][2]
        # time_data_vibe = values_list[0][1][6][8][2]
        for data_point in range(len(values_list[0][1][0][14][2])):

            # Checks that the correct amount has been added to the time column
            self.assertEqual((values_list[0][1][0][14][2][data_point] + time_x_offset[0]),
                             values_list_offset[0][0][14][2][data_point])

        for data_point in range(len(values_list[0][1][6][7][2])):
            # Checks that the correct amount has been added to the time column
            self.assertEqual((values_list[0][1][6][7][2][data_point] + time_x_offset[0]),
                             values_list_offset[0][6][7][2][data_point])

    def test_select_plot_data_single(self):
        """Tests for select_plot_data_single()"""
        # Assign variables
        plot_information = [["x", "time", "gps"], ["y", "altitude", "gps"]]
        print("TEST START")
        # Changes the values list to only include the data
        values_list, flight_dates_list, single_flight, number_of_flights =\
            plotting.single_flight_detection(self.values_list)

        # Runs the method
        plot_data = plotting.select_plot_data_single(values_list, plot_information, number_of_flights)

        # Checks that the called data is correct
        for data_index in range(len(values_list[0][0][14][2])):
            # time_data_gps = values_list[0][0][14][2]
            self.assertEqual(values_list[0][0][14][2][data_index], plot_data[0][0][1][2][data_index])
            # altitude_data_gps = values_list[0][0][8][2]
            self.assertEqual(values_list[0][0][8][2][data_index], plot_data[0][1][1][2][data_index])

    def test_arm_data_formatting(self):
        pass

    def test_single_flight_detection(self):
        pass


if __name__ == '__main__':
    unittest.main()
