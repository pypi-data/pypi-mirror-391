import numpy as np
import matplotlib.pyplot as plt

from marge3d.numeric import NumericalSolver
from marge3d.fields import VelocityField3D

from marge3d.params import DaitcheParameters

R0     = np.array([1, 0, 0])
W0     = np.array([0, 0, 0])

particle_density    = 1410
fluid_density       = 972
particle_radius     = 0.0015
kinematic_viscosity = 2 * 1e-4
time_scale          = 0.0125
char_vel            = 0.4

par = DaitcheParameters(particle_density, fluid_density, particle_radius,
                    kinematic_viscosity, time_scale, char_vel)

print("G = ", par.g)
print("R = ", par.R)
print("S = ", par.S)

order  = 2
T_ini  = 0
T_fin  = 10
T      = T_fin - T_ini
Vortex = VelocityField3D(1)

V0    = Vortex.get_velocity(R0[0], R0[1], R0[2], T_ini)
N     = 100

Order_n = NumericalSolver(R0, W0, Vortex, N, order, particle_density, fluid_density, particle_radius,
                   kinematic_viscosity, time_scale, char_vel)

t_v = np.linspace(T_ini, T_fin, N)
if order == 1:
    R_x, R_y, R_z, W = Order_n.Euler(t_v, flag=True)
elif order == 2:
    R_x, R_y, R_z, W = Order_n.AdamBashf2(t_v, flag=True)
elif order == 3:
    R_x, R_y, R_z, W = Order_n.AdamBashf3(t_v, flag=True)
else:
    raise ValueError("Order must be 1, 2, or 3.")

#"""
# For quiver plot of the fluid field
x, y, z = np.meshgrid(
    np.linspace(-1.5, 1.5, 5),
    np.linspace(-1.5, 1.5, 5),
    np.linspace(-0.21, 0, 5)
)

u, v, w = Vortex.get_velocity(x, y, z, T_fin)

fig = plt.figure()
# size of the figure
fig.set_size_inches(5, 5)
ax = fig.add_subplot(111, projection='3d')

# Plot the 3D line
plt.plot(R_x, R_y, R_z, color="blue", label='Numerical solution')
ax.scatter(1, 0, 0, color='green', label='Initial position')
ax.quiver(x, y, z, u, v, w, length=0.25, normalize=True, arrow_length_ratio=0.1, alpha=0.5)

# Add labels
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

# Add a legend
ax.legend(loc='upper right', bbox_to_anchor=(1, 0.9))

# Show the plot
ax.set_box_aspect(None, zoom=0.8)

plt.show()
