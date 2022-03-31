"""
This module contains various physics and mathematics relationships
"""
import  numpy as np

def minnaert_radius(freq, depth):
    """
    Calculates the minneart radius for a spherical bubble in water
    """
    # https://www.engineeringtoolbox.com/specific-heat-capacity-gases-d_159.html
    gamma = 1.405 # taken from website above for 300K
    rho = 997 # kg/m^3 density of water
    PA = (rho * 9.8 * depth) + 100000 # kg/(m*s^2)
    # PA/rho => PA(kg*m^-1*s^-2) / rho(kg * m^-3) =? PA(...) * rho(kg^-1 * m^3) => m^2 * s^-2
    return (2 * np.pi * freq)**(-1) * ((3 * gamma * PA)/(rho))**(1/2)

def ideal_gas_n(pressure, volume):
    """
    returns the number of moles given the pressure and volume
    
    temperature is average temperature in BA1B
    """
    P = pressure
    V = volume
    R = 8.31446261815324 # J K^−1 mol^−1
    T = 34.75 + 273.15 # K
    n = (P * V)/(R * T)
    return n