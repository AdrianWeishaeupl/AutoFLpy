# -*- coding: utf-8 -*-
"""
Generates the xls file name
"""


def excel_file_name_updater(dates, flight_numbers):
    """Takes a list of dates and a list of flight numbers and returns a list of names"""
    flight_names = []
    if len(dates) == len(flight_numbers):
        for flight in range(len(dates)):
            # Checks to see if the year data is in the right format
            date = str(dates[flight])
            if len(date) != 8:
                raise Exception("The date is in an incorrect format. Format should be YYYYMMDD. date = {}".format(date))
            year = date[:4]
            month = date[4:6]
            day = date[6:]
            try:
                int(year)
                year_available = True
            except ValueError:
                year_available = False
            # Appends result to check_data list
            # Checks to see if the month data is in the right format
            try:
                int(month)
                month_available = True
            except ValueError:
                month_available = False
            # Appends result to check_data list
            # Checks to see if the day data is in the right format
            try:
                int(day)
                day_available = True
            except ValueError:
                day_available = False
            # Appends result to check_data list
            # Puts the month in the correct format
            if len(month) < 2:
                month = "0" + month
            # Puts the day in the correct format
            if len(day) < 2:
                day = "0" + day
            # Ensures the year is returned in the correct format
            if len(year) < 4:
                year = "20" + year
            # Gets the flight date from the input data.
            flight_date = int((year + month + day).replace("\n", ""))
            # Gets the flight number from the input data.
            try:
                # Checks to see if the flight number is available
                flight_number = int(flight_numbers[flight])
                flight_number_available = True
                if len(str(flight_number)) < 2:
                    flight_number = "0" + str(flight_number)
            except ValueError:
                # If it is not then the flight number is returned as False.
                flight_number_available = False
            # Checks to see if the flight date is available
            if (year_available and month_available and day_available) is True:
                text = str(flight_date) + "_Flight"
                # Checks to see if the flight number is available
                if flight_number_available is True:
                    text += flight_number
                else:
                    # Error message explaining that data is required
                    raise Exception("Error", "Flight number is required for"
                                    " the automatic generation of the excel"
                                    " file name.")
                    # Sets textbox to be blank.
                    text = ""
            else:
                raise Exception("Error", "The complete flight date is required"
                                " for the automatic generation of the excel"
                                " file name.")
                # Sets textbox to be blank.
                text = ""
            # If nothing entered, do not clear the text box.
            if text == "":
                return
            flight_names.append(text)

        # Outputs generated file names for reading in the Flight Log Code.
        global generated_file_name
        print(type(flight_names))
        generated_file_name = flight_names
    else:
        raise IndexError("Number of dates does not match the number of flights. Check the Input_file.json to make sure"
                         " the lists are of the same length. len(dates) = {}, len(flight_numbers) ="
                         " {}".format(len(dates), len(flight_numbers)))
    return generated_file_name
