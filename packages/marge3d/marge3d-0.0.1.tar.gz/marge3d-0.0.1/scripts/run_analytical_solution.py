#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analytic solution and numerical solution will agree only when
time_scale is 0.1 and char_vel is 0.4.
This is because the analytical solution is derived under these conditions.
Other parameters can be changed.
"""
import numpy as np
import matplotlib.pyplot as plt

from marge3d.fields import VelocityField3D
from marge3d.numeric import NumericalSolver
from marge3d.analytic import AnalyticalSolver


particle_density    = 500
fluid_density       = 972
particle_radius     = 0.0015 # S=0.3 for this and the 3rd order method does not perform well. So the solution trajectories are obtained for order 2 method.
kinematic_viscosity = 2 * 1e-4
time_scale          = 0.1
char_vel            = 0.4

order  = 2
T      = 10
h      = 0.01 #Somehow if I take h<0.01, the numerical solution does not converge, it becomes unstable.
#This happens only when we use the characteristic velocity=0.4 and time scale=0.1.
N      = 1000

R0     = np.array([1, 0, 0])
W0     = np.array([0, 0, 0])

Vortex = VelocityField3D(10*time_scale)
t_v   = np.linspace(0, T, N)
#t_v    = np.arange(0, T, h)

U0    = Vortex.get_velocity(R0[0], R0[1], R0[2], 0) # Initial fluid velocity

MRE_analytic = AnalyticalSolver(R0, U0, particle_density, fluid_density, particle_radius, kinematic_viscosity, time_scale, char_vel)

Order_n = NumericalSolver(R0, W0, Vortex, len(t_v), order, particle_density, fluid_density, particle_radius,
                   kinematic_viscosity, time_scale, char_vel)

if order == 1:
    R_x, R_y, R_z, W = Order_n.Euler(t_v, flag=True)
elif order == 2:
    R_x, R_y, R_z, W = Order_n.AdamBashf2(t_v, flag=True)
elif order == 3:
    R_x, R_y, R_z, W = Order_n.AdamBashf3(t_v, flag=True)
else:
    raise ValueError("Order must be 1, 2, or 3.")

X      = np.zeros(len(t_v))
Y      = np.zeros(len(t_v))
Z      = np.zeros(len(t_v))

for i in range(len(t_v)):
    X[i], Y[i] = MRE_analytic.solve(t_v[i])
    Z[i]       = MRE_analytic.solve_z(t_v[i])

#"""
# For quiver plot of the fluid field
x, y, z = np.meshgrid(
    np.linspace(-1.5, 1.5, 5),
    np.linspace(-1.5, 1.5, 5),
    np.linspace(0, 0.27, 5)
)
#"""

u, v, w = Vortex.get_velocity(x, y, z, T)

#'''
fig = plt.figure()
fig.set_size_inches(5, 5)
ax = fig.add_subplot(111, projection='3d')

# Plot the 3D line
plt.plot(X, Y, Z, label="Analytical solution", color="red")
#plt.plot(R_x, R_y, R_z, label="Numerical solution", color="blue")
plt.plot(R_x[0::50], R_y[0::50], R_z[0::50], 'x', label = "Numerical solution", color="blue")
ax.scatter(1, 0, 0, color='green', label='Initial position')
ax.quiver(x, y, z, u, v, w, length=0.25, normalize=True, arrow_length_ratio=0.1, alpha=0.5)

# Add labels
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

# Add a legend
ax.legend(loc='upper right', bbox_to_anchor=(1, 0.9))

ax.set_box_aspect(None, zoom=0.8)

# Show the plot
plt.show()