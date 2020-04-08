"""
This code processes weather data.

@author Adrian Weishaeupl
aw6g15@soton.ac.uk 2019

"""

import pandas as pd
import scipy.constants as co
from ADRpy import unitconversions as uc


def environmental_data_filtering(values_list):
    """A method for returning the environmental data from a values_list data set
    returns data in a list of [weather_data, runway_data, flight] entries"""
    data_set = []
    number_of_flights = len(values_list)
    for flight in range(number_of_flights):
        values_list_dataframe = pd.DataFrame(values_list[flight][1])
        index = values_list_dataframe[0]  # Creates a set of titles to be written over the titles present
        transposed_values_list_dataframe = values_list_dataframe.transpose()[1:]  # Removes the old titles
        data_only = transposed_values_list_dataframe.transpose()  # Turns the data frame to index the columns
        # Indexes the columns and turns the data frame so that they can be called:
        data_with_index = data_only.set_index(index).transpose()
        # Calls the data
        runway_data = list(data_with_index["RUNWAY"])
        weather_data = list(data_with_index["WEATHER"])
        aircraft_data = list(data_with_index["AIRCRAFT"])
        data_set.append([weather_data, runway_data, aircraft_data, values_list[flight][0]])
    return data_set


def environmental_data_dictionary(values_list, index):
    """Designed for the weather data (index = 0) and runway data (index = 1)

    Returns a dictionary data set in the form:
    [[dictionary_1, flight_1], [dictionary_2, flight_2]]
    """
    data_set = environmental_data_filtering(values_list)
    data_list = []
    number_of_flights = len(values_list)
    # Runs through the number of flights and creates a dictionary for each flight
    for flight in range(number_of_flights):
        data = {}
        data_raw = data_set[flight][index]
        for entry in data_raw:
            if entry is not None and "dummy" not in entry[0].lower():
                name = str(entry[0]) + "_" + str(entry[1])
                name = name.replace(" ", "_")
                data_value = entry[-1][0]  # the [0] is to return just the element (not a list)
                data[name] = data_value
        if index == 0:
            # Additional data calculations for weather data
            data["Density_kgperm3"] = data["Pressure_Pa"]/(287. * uc.c2k(data["Temperature_C"]))
        data_list.append([data, values_list[flight][0]])
    return data_list


def weather_data_dictionary(values_list):
    """Creates a list of dictionary of weather_data from a values_list. One dictionary is created per flight

    returns
        [[weather_dictionary_1, flight_1], [weather_dictionary_2, flight_2]]
        where weather_dictionary is a dictionary of weather data"""
    return environmental_data_dictionary(values_list, 0)


def runway_data_dictionary(values_list):
    """Creates a list of dictionary of runway_data from a values_list. One dictionary is created per flight

    returns
        [[runway_dictionary_1, flight_1], [runway_dictionary_2, flight_2]]
        where runway_dictionary is a dictionary of runway data"""
    return environmental_data_dictionary(values_list, 1)


def aircraft_data_dictionary(values_list):
    """Creates a list of dictionary of aircraft_data from a values_list. One dictionary is created per flight

    returns
        [[aircraft_dictionary_1, flight_1], [aircraft_dictionary_2, flight_2]]
        where aircraft_dictionary is a dictionary of aircraft data"""
    return environmental_data_dictionary(values_list, 2)
