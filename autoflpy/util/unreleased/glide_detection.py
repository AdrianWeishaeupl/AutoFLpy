"""
This code detects when a UAV is gliding under no power.

@author Adrian Weishaeupl
aw6g15@soton.ac.uk 2019

"""

import scipy.constants as co
import numpy as np
import pandas as pd
from autoflpy.util.analysis.environmental_data_processing import *


def glide_detection(values_list):
    """This code detects when a UAV is gliding and returns the glide slope angle from the horizontal in degrees"""
    glide_slope_deg, v_tas_mps = 0, 0  # TODO This needs defining

    return glide_slope_deg, v_tas_mps


def cl_cd_glide_slope_calculator(values_list, mass):
    """Calculates the C_L and C_D of a UAV given flight data"""
    weather_data = weather_data_dictionary(values_list)[0][0]
    glide_slope_deg, v_tas_mps = glide_detection(values_list)
    weight_n = co.g * mass
    rho_sl_kgperm3 = weather_data["Density_kgperm3"]
    q_sl = 0.5 * rho_sl_kgperm3

    lift_n = weight_n * np.cos(np.radians(glide_slope_deg))
    drag_n = -1. * weight_n * np.sin(np.radians(glide_slope_deg))

    # Converts lift and drag to non-dimensional coefficients

    pass
