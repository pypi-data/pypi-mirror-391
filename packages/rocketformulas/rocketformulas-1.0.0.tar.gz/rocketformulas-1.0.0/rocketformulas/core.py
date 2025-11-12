"""
rocketformulas
==============

A Python library providing basic formulas for rocket engine analysis.

Author: Amandeep Singh
Version: 1.0.0
License: MIT

🧭 Description:
---------------
This module provides a collection of fundamental rocket propulsion equations 
used for preliminary rocket engine design and performance estimation.
"""

import math

# Constants
g0 = 9.80665  # standard gravity (m/s^2)
R = 8314.5    # universal gas constant (J/kmol·K)

# 1. Thrust Calculation
def thrust(m_dot, v_e, p_e, p_a, A_e):
    """
    Calculate thrust produced by a rocket engine.
    
    Parameters:
        m_dot : float - mass flow rate (kg/s)
        v_e   : float - exhaust velocity (m/s)
        p_e   : float - exit pressure (Pa)
        p_a   : float - ambient pressure (Pa)
        A_e   : float - exit area (m^2)
    
    Returns:
        float - thrust (N)
    """
    return m_dot * v_e + (p_e - p_a) * A_e

# 2. Specific Impulse
def specific_impulse(thrust, m_dot):
    """
    Calculate specific impulse (Isp).
    
    Parameters:
        thrust : float - thrust (N)
        m_dot  : float - mass flow rate (kg/s)
    
    Returns:
        float - specific impulse (s)
    """
    return thrust / (m_dot * g0)

# 3. Mass Flow Rate (given thrust and exhaust velocity)
def mass_flow_rate(thrust, v_e, p_e=0, p_a=0, A_e=0):
    """
    Calculate mass flow rate for a given thrust and exhaust velocity.
    """
    return (thrust - (p_e - p_a) * A_e) / v_e

# 4. Exhaust Velocity (from specific impulse)
def exhaust_velocity(Isp):
    """
    Calculate exhaust velocity from specific impulse.
    """
    return Isp * g0

# 5. Effective Exhaust Velocity (including pressure thrust)
def effective_exhaust_velocity(v_e, p_e, p_a, A_e, m_dot):
    """
    Calculate effective exhaust velocity accounting for pressure difference.
    """
    return (m_dot * v_e + (p_e - p_a) * A_e) / m_dot

# 6. Characteristic Velocity (c*)
def characteristic_velocity(p_c, A_t, m_dot):
    """
    Calculate characteristic velocity (c*).
    
    Parameters:
        p_c  : float - chamber pressure (Pa)
        A_t  : float - throat area (m^2)
        m_dot: float - mass flow rate (kg/s)
    
    Returns:
        float - characteristic velocity (m/s)
    """
    return p_c * A_t / m_dot

# 7. Thrust Coefficient (Cf)
def thrust_coefficient(thrust, p_c, A_t):
    """
    Calculate thrust coefficient.
    """
    return thrust / (p_c * A_t)

# 8. Nozzle Exit Mach Number
def exit_mach_number(gamma, p_e, p_c):
    """
    Calculate Mach number at nozzle exit using isentropic relation.
    """
    term = (p_c / p_e) ** ((gamma - 1) / gamma)
    M_e = math.sqrt((2 / (gamma - 1)) * (term - 1))
    return M_e

# 9. Exit Pressure (isentropic expansion)
def exit_pressure(p_c, gamma, M_e):
    """
    Calculate exit pressure given chamber pressure and exit Mach number.
    """
    return p_c / ((1 + ((gamma - 1) / 2) * M_e ** 2) ** (gamma / (gamma - 1)))

# 10. Ideal Exhaust Velocity (isentropic)
def ideal_exhaust_velocity(gamma, R_specific, T_c, p_e, p_c):
    """
    Calculate ideal exhaust velocity (isentropic expansion).
    
    Parameters:
        gamma      : float - ratio of specific heats
        R_specific : float - gas constant (J/kg·K)
        T_c        : float - chamber temperature (K)
        p_e, p_c   : float - exit and chamber pressures (Pa)
    """
    term = (2 * gamma / (gamma - 1)) * R_specific * T_c * (1 - (p_e / p_c) ** ((gamma - 1) / gamma))
    return math.sqrt(term)
