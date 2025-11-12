# 🚀 rocketformulas

A Python library for basic rocket engine performance formulas.

## Example
```python
import rocketformulas as rf

# Example inputs
m_dot = 5
v_e = 2500
p_e = 101325
p_a = 90000
A_e = 0.2
p_c = 3e6
A_t = 0.05

# Compute values
T = rf.thrust(m_dot, v_e, p_e, p_a, A_e)
Isp = rf.specific_impulse(T, m_dot)
mfr = rf.mass_flow_rate(T, v_e, p_e, p_a, A_e)
ve = rf.exhaust_velocity(Isp)
c_star = rf.characteristic_velocity(p_c, A_t, m_dot)

# Print everything
print(f"Thrust: {T:.2f} N")
print(f"Specific Impulse: {Isp:.2f} s")
print(f"Mass Flow Rate: {mfr:.2f} kg/s")
print(f"Exhaust Velocity: {ve:.2f} m/s")
print(f"Characteristic Velocity: {c_star:.2f} m/s")

## Example
```python
import numpy as np
import matplotlib.pyplot as plt
import rocketformulas as rf

# Define parameters
m_dot = 5               # kg/s
p_e = 101325            # Pa
p_a = 90000             # Pa
A_e = 0.2               # m^2

# Range of exhaust velocities
v_e_values = np.linspace(1500, 3500, 10)

# Calculate thrust for each exhaust velocity
thrust_values = [rf.thrust(m_dot, v, p_e, p_a, A_e) for v in v_e_values]

# --- Plot using Matplotlib ---
plt.figure(figsize=(8, 5))
plt.plot(v_e_values, thrust_values, marker='o', linewidth=2)

# Labels and title
plt.title("Rocket Engine Thrust vs Exhaust Velocity", fontsize=14)
plt.xlabel("Exhaust Velocity (m/s)", fontsize=12)
plt.ylabel("Thrust (N)", fontsize=12)
plt.grid(True)

# Show the plot
plt.show()
