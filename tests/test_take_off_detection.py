# -*- coding: utf-8 -*-
"""
Unit tests for the take_off_detection module
Created on Tue Feb 18 14:53:20 2020

@author Adrian Weishaeupl (aw6g15@soton.ac.uk)
"""

from autoflpy.util.analysis import take_off_detection
import unittest
import os
import pickle as pk


def load_values_list_from_pickle(data_file_path):
    # Uncompress the data.
    data = open(data_file_path, "rb")
    values_list = pk.load(data)
    data.close()
    return values_list


class TestTakeOffDetection(unittest.TestCase):

    def setUp(self):
        self.base_path = os.path.join(os.path.dirname(__file__),
                                      "test_files") + os.sep
        self.base_path = self.base_path.replace(os.sep, "/")
        self.values_list = load_values_list_from_pickle(self.base_path + "test_pickled_data.pkl")

    def test_take_off_point_finder(self):
        """Tests the take_off_point_finder"""
        # Generates the data
        values_list = self.values_list

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

        expected_take_off_time_alt_list = [33.21, 33.41, 33.61, 34.41, 34.81]
        expected_take_off_groundspeed_list = [20.25, 21.47, 22.54, 25.42, 26.30]
        expected_take_off_time_spd_list = [30.81, 30.81, 31.01, 31.41, 31.61]

        # Compares the generated values to the expected values
        for item in range(len(sensitivity_list)):
            self.assertEqual(take_off_groundspeed_list[item], expected_take_off_groundspeed_list[item])
            self.assertEqual(take_off_time_alt_list[item], expected_take_off_time_alt_list[item])
            self.assertEqual(take_off_time_spd_list[item], expected_take_off_time_spd_list[item])

    def test_significant_data_change_via_rms_error(self):
        """Unit test for the significant_data_change_via_rms_error"""
        values_list = self.values_list  # Imports values to be used
        # values_list[0] is the GPS data set
        # values_list[0][x] is a single set of data as [descriptor, units, [data]]
        # values_list[0][x][2] is a single set of data
        data_set_altitude = values_list[0][1][0][8]
        data_set_groundspeed = values_list[0][1][0][9]
        data_sets = [data_set_altitude, data_set_groundspeed]

        constant_value_points_list = []
        mean_list = []
        data_point_list = []
        rms_error_list = []

        sensitivities = [0.05, 0.1, 0.2, 0.5, 0.7]
        for sensitivity in sensitivities:
            for data_set in data_sets:
                constant_value_points, mean, data_point, rms_error = \
                    take_off_detection.significant_data_change_via_rms_error(data_set[2], sensitivity)
                constant_value_points_list.append(constant_value_points)
                mean_list.append(mean)
                data_point_list.append(data_point)
                rms_error_list.append(rms_error)

        lists = [mean_list, data_point_list, rms_error_list]
        expected_data = [[8.388690476190476, 0.0034166666805555555, 8.396235294117647, 0.0034166666805555555,
                          8.410813953488372, 0.01558904110958904, 8.551666666666668, 0.08913333334666666,
                          8.678152173913045, 0.15988157896052632],
                         [84, 72, 85, 72, 86, 73, 90, 75, 92, 76],
                         [0.06874143389818238, 0.10257614404379453, 0.1336248679103539, 0.10257614404379453,
                          0.20551288210907936, 0.22779510268712833, 0.5493127740558753, 0.6086535257834387,
                          0.7469731708072621, 0.8356314669674233]]

        # Checks that all the items generated are correct. The constant_value_points_list is omitted for brevity
        for list_item in range(len(lists)):
            for item in range(len(lists[list_item])):
                self.assertEqual(lists[list_item][item], expected_data[list_item][item])


if __name__ == '__main__':
    unittest.main()
