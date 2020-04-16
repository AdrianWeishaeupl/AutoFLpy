"""
This code detects when a UAV is gliding under no power.

@author Adrian Weishaeupl
aw6g15@soton.ac.uk 2019

"""

import scipy.constants as co
import numpy as np
from autoflpy.util.analysis.environmental_data_processing import *


def glide_detection(values_list):
    """This code detects when a UAV is gliding and returns the glide slope angle from the horizontal in degrees"""
    glide_slope_deg, v_tas_mps = -10, 30  # TODO This needs defining

    return glide_slope_deg, v_tas_mps


def cl_cd_glide_slope_calculator(values_list):
    """Calculates the C_L and C_D of a UAV given flight data"""
    weather_data = weather_data_dictionary(values_list)[0][0]  # TODO: [0][0] currently looks at first flight only
    aircraft_data = aircraft_data_dictionary(values_list)[0][0]
    glide_slope_deg, v_tas_mps = glide_detection(values_list)
    mtot_kg = aircraft_data["M_empty_kg"] + aircraft_data["M_fuel_kg"]  # TODO: Mass will reduce in the flight
    weight_n = co.g * (mtot_kg)
    rho_sl_kgperm3 = weather_data["Density_kgperm3"]
    s_m2 = aircraft_data["S_m2"]


    lift_n = weight_n * np.cos(np.radians(glide_slope_deg))
    drag_n = -1. * weight_n * np.sin(np.radians(glide_slope_deg))

    # Converts lift and drag to non-dimensional coefficients
    cl = 2 * lift_n/(rho_sl_kgperm3 * v_tas_mps ** 2 * s_m2)
    cd = 2 * drag_n / (rho_sl_kgperm3 * v_tas_mps ** 2 * s_m2)

    return cl, cd
