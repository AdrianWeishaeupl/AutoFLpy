import numpy as np


def take_off_point_finder(values_list, alt_sensitivity=0.3, groundspeed_sensitivity=0.3):
    """Finds the take-off point from the gps flight data from an RMS approach.

    The sensitivity is used to define the point where the data deviates from a linear trend (on the runway).
    Sensitivities need to be adjusted for the data for more accurate times.

    The same method is also used on the gps groundspeed data to give an idea of the take-off run.

    Returns:    take_off_time_alt (take-off time from the altitude data),
                take_off_groundspeed (at the altitude take-off time),
                take_off_time_spd (take-off time from the groundspeed data i.e. start of the take-off run)"""

    # Imports GPS data
    gps_index = [["altitude", "gps"], ["groundspeed", "gps"], ["time", "gps"]]
    gps_data = []

    for index in gps_index:
        values_list_index = 0
        # sets value_found to a default of False
        # Checks to see if the 'data source' recorded in the graph list
        # matches the 'data sources' in the list structure values_list.
        for values_list_data in values_list[0][1]:
            # Finds data source.
            if index[1] == values_list_data[0].lower():
                index.append(values_list_index)
                # Finds corresponding time source.
                # Goes through each column searching for a match.
                for column in values_list[0][1][values_list_index][1:]:
                    # Checks to see if they have the same title.
                    if column[0].lower() == index[0]:
                        # if they do then the data is appended.
                        gps_data.append(column)
                        # exits for loop if data has been appended.
                        break
            values_list_index += 1

    # find the runway altitude from the initial altitude points and uses a root mean squared error to determine the
    # point of unacceptable altitude variation (take-off).
    alt_data = gps_data[0][2]

    # Finds the first take-off point by evaluating the developing mean and root mean squared error
    ground_alt_data, mean_ground_alt, take_off_data_point_alt, alt_error = \
        significant_data_change_via_rms_error(alt_data, alt_sensitivity)

    take_off_time_alt = gps_data[2][2][take_off_data_point_alt]
    take_off_groundspeed = gps_data[1][2][take_off_data_point_alt]

    # Repeats the process for groundspeed
    spd_data = gps_data[1][2]
    ground_spd_data, mean_ground_spd, take_off_data_point_spd, spd_error = \
        significant_data_change_via_rms_error(spd_data, groundspeed_sensitivity)

    take_off_time_spd = gps_data[2][2][take_off_data_point_spd]

    return round(take_off_time_alt, 2), round(take_off_groundspeed, 2), round(take_off_time_spd, 2)


def significant_data_change_via_rms_error(data_set, sensitivity=0.3):
    """Finds the first point that significantly deviates from a constant value trend. This uses a developing root mean
        squared error and compares it to a prescribes sensitivity.

    Input: significant_data_change_via_rms_error(data_set, sensitivity)
        where   data_set is a list of data to be analysed
                sensitivity is the sensitivity with which the deviation is determined

    Returns the constant_value_points list, mean(constant_value_points), the data point at which the deviation
        occurs and the final rms_error
     """
    # find the runway altitude from the initial altitude points and uses a root mean squared error to determine the
    # point of unacceptable data variation.
    rms_error = 0
    data_point = 0
    constant_value_points = []

    # Finds the first deviation point by evaluating the developing mean and root mean squared error
    while rms_error < sensitivity:
        constant_value_points.append(data_set[data_point])
        data_point = data_point + 1
        mean = np.mean(constant_value_points)
        rms_error = 0
        # Finds a root mean squared error for the current list
        for item in constant_value_points:
            rms_error = np.sqrt(((mean - item)**2)/data_point)

    # Removes the error exceeding argument to give just points in the constant segment of data.
    constant_value_points.pop()
    data_point -= 1  # Last data point on the ground

    return constant_value_points, np.mean(constant_value_points), data_point, rms_error
