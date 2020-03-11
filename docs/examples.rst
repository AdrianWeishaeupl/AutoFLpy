Examples
========

The following section contains examples on how to use the Jupyter Notebook generated through AutoFLpy.

Graph Plotter Examples
----------------------

Once AutoFLpy has been run, a Jupyter Notebook is generated. This can be opened using Jupyter Notebook and run to generate the requested graphs.

The graph plotter is used to plot simple data such as the following altitude plot:

.. image:: images/Ex_alt_v_time_1.png
	:width: 900
	:alt: Image of a graph generated with AutoFLpy showing altitude plotted against time.

The code cell above the graph is used to define variables used in the plot such as the axes limits and variables used in the function itself. The axes limits (x_limits and y_limits) can be changed and the code re-run to generate a view of a more precise section of the plot:

.. image:: images/Ex_alt_v_time_2.png
	:width: 900
	:alt: Image of a graph generated with AutoFLpy showing a section of the altitude v time plot.

Variables in the same data group (in this case "gps") can be plotted on the same graph either by changing the notebook template (recommended) or by inserting the data tag (eg. ["y", "groundspeed", "gps"]) into the function:

.. image:: images/Ex_alt_v_time_3.png
	:width: 900
	:alt: Image of a graph generated with AutoFLpy showing altitude and groundspeed v time.

If two variables are from different data sets, there is a good chance that they were sampled at different frequencies. For this, the multiaxes plotter function can be used. This function works under the same principle as the function mentioned above but allows for several data sets to be plotted:

.. image:: images/Ex_arsp_alt_v_time_1.png
	:width: 900
	:alt: Image of a graph generated with AutoFLpy showing altitude and airspeed v time.

The arm and disarm times can be added to both multi-variable and standard graphs. This is done through the addition of the arm_data variable. The time between the arm and disarm will also be calculated:

.. image:: images/Ex_alt_v_time_4.png
	:width: 900
	:alt: Image of a graph generated with AutoFLpy showing the altitude v time plot as well as the times when it was armed and disarmed.

For marking specific flight points across all graphs simultaneously, define your markers in the marker_list as a list of numbers. Below is an example marking the two highest points in the flight on the altitude figure and displaying these in the airspeed and groundspeed figure.

.. image:: images/Ex_markers.png
	:width: 900
	:alt: Image of a graph generated with AutoFLpy showing the use of custom markers on various plots.


Plotting Maps
-------------

This is a special feature of the graph plotter and allows for a top down visualisation of the flight and surrounding area. To activate this feature, plot latitude against longitude. Two maps will be generated, one of the immediate flight area and one of the region:

.. image:: images/Ex_map_1_code.png
	:width: 900
	:alt: Image of input to the graph plotter to gerenate a map.

.. image:: images/SITL_flight_map.png
	:width: 900
	:alt: Image of zoomed in map generated using Software In The Loop.

.. image:: images/SITL_flight_map_out.png
	:width: 900
	:alt: Image of zoomed in map generated using Software In The Loop.

The scale of the second plot can be changed through the addition of the scale variable:

.. image:: images/Ex_map_2_code.png
	:width: 900
	:alt: Image of input to the graph plotter to gerenate a map with a scale defined.

.. image:: images/SITL_flight_map_out_2.png
	:width: 900
	:alt: Image of zoomed in map generated using Software In The Loop.

The colour of the additional variable on the map plot can be defined by any third varible for which data is present. This is done through the addition of the map_info variable. The following examplke demonstrates this with airspeed:

.. image:: images/Ex_map_3_code.png
	:width: 900
	:alt: Image of input to the graph plotter to gerenate a map with airspeed on the colour axes.

.. image:: images/SITL_flight_map_3.png
	:width: 900
	:alt: Image of zoomed in map generated using Software In The Loop showing airspeed on the colour axes.

To set limits in the map plot, the map_info_limits argument can be used. map_info_limits are limits to be applied in to the map_info data in the form [lower_limit, upper_limit]. If only one limit is required, enter the other limit as None. This colours any points below the lower_limit in blue and any above the upper_limit in red. Below is an example with altitudes below 25 m and above 85 m marked.

.. image:: images/SITL_flight_map_4.png
	:width: 900
	:alt: Image of zoomed in map generated using Software In The Loop showing outliers marked.

Take-off Graphs
---------------

Take-off graphs can be generated using the take_off_graph function. This allows the user to quickly plot the variables that influence the take off of the UAV. In it's most basic form, this function detects the take off and plots 5 figures focused around the take-off. The take off point is gound using the GPS data provided. If the function does not automatically detect the take off it can be entered manually using the take_off_time argument. Sensitivity of the take-off detection can be adjusted in the alt_sensitivity and groundspeed_sensitivity arguments. Markers and arm data work as normally described.

The following figure shows the use of this feature.

.. image:: images/Ex_take_off.png
	:width: 900
	:alt: Image of the take off data plotted through the take_off_graph function.


Multiple Flight Comparison
--------------------------

Autoflpy allows for the user to compare multiple flights in the same Jupyter Notebook. To do this, data should be entered into the Input_File.json for each flight separated by a ",". For example::

	"log_to_xlsx_input": {
			"log_file_name": "Flight1.log, Flight2.log",
			"log_file_path": "",
			"excel_data_file_path": "",
			"date": "20190309, 20190209",
			"flight_number": "1, 2"}

Variables are entered into the plotting functions as usual and plotted for both sets of data if present. Some functionality is reduced including the automated take-off detection (reverted to manual only) and plotting the arm data when plotting multiple flights simultaneously.

To aid with the lining up of data, the time_x_offset argument can be added to the plot to allow the user to shift the data along the time axis. It should only be used in the first figure to be plotted and, as it directly edits the imported data, all subsequent figures will be plotted with the new data. This argument takes one number for each flight being plotted and subtracts this from the time data:

.. image:: images/Ex_time_x_offset.png
	:width: 900
	:alt: Image of two simulated flights with the time axes shifted through the time_x_offset argument.

