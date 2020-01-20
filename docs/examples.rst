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


