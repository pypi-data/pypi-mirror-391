"""
###############################################################################
################################Convergence test###############################
###############################################################################
Particle initial velocity is set to be equal to the initial fluid velocity.
This is according to the paper by Candelier et al.
"""
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor

from marge3d.fields import VelocityField3D
from marge3d.numeric import NumericalSolver
from marge3d.analytic import AnalyticalSolver

# -----------------------------------------------------------------------------
# Parameters
# -----------------------------------------------------------------------------
particle_density    = 500
fluid_density       = 972
particle_radius     = 0.00018**0.5  # 0.0135
kinematic_viscosity = 2 * 1e-4
time_scale          = 0.1
char_vel            = 0.4

St = (particle_radius**2.0) * 1 / (3 * kinematic_viscosity*time_scale)
print("Stokes number (S) = ", St)

# -----------------------------------------------------------------------------
# Initial conditions
# -----------------------------------------------------------------------------
R0     = np.array([1, 0, 0])
Vortex = VelocityField3D(1)
U0     = Vortex.get_velocity(R0[0], R0[1], R0[2], 0) # Initial fluid velocity
V0     = np.array(Vortex.get_velocity(R0[0], R0[1], R0[2], 0)) # Same as initial fluid velocity
W0     = V0 - U0 # Relative velocity

MRE_analytic = AnalyticalSolver(R0, U0, particle_density, fluid_density,
                                       particle_radius, kinematic_viscosity, time_scale, char_vel)

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def analytic_traj(t):
    """Analytical position at time t."""
    sol = MRE_analytic.solve(t)
    return np.array([sol[0], sol[1], MRE_analytic.solve_z(t)])

def Err_n(t, N, order):
    """Compute L_inf error for given N and order."""
    t_v = np.linspace(0, t, N)
    mre = NumericalSolver(R0, W0, Vortex, N+1, order, particle_density, fluid_density, particle_radius,
                       kinematic_viscosity, time_scale, char_vel)
    if order == 1:
        R_x, R_y, R_z, W = mre.Euler(t_v, flag=True)
    elif order == 2:
        R_x, R_y, R_z, W = mre.AdamBashf2(t_v, flag=True)
    elif order == 3:
        R_x, R_y, R_z, W = mre.AdamBashf3(t_v, flag=True)
    else:
        raise ValueError("Order must be 1, 2, or 3")

    R_num = np.column_stack((R_x, R_y, R_z))
    R_ana = np.array([analytic_traj(ti) for ti in t_v])
    return np.max(np.linalg.norm(R_ana - R_num, axis=1))


# -----------------------------------------------------------------------------
# Compute errors
# -----------------------------------------------------------------------------
def _err_worker(args):
    """Worker function for parallel error computation."""
    return Err_n(*args)

def compute_all_errors(N_v, t_end=1.0):
    with ProcessPoolExecutor() as ex:
        results = list(ex.map(
            _err_worker,
            [(t_end, N, order) for N in N_v for order in [1, 2, 3]]
        ))
    results = np.array(results).reshape(len(N_v), 3)
    return (*results.T,)


# -----------------------------------------------------------------------------
# Main script
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    N_v = np.logspace(np.log10(10), np.log10(1000), num=20).astype(int)
    Err_v1, Err_v2, Err_v3 = compute_all_errors(N_v)

    plt.figure(figsize=(5.5, 4))
    lw, ms = 2.0, 6
    colors = ["blue", "orange", "green"]

    for Err, order, color in zip([Err_v1, Err_v2, Err_v3],
                                [1, 2, 3], colors):
        plt.plot(N_v, Err, 'o-', color=color, lw=lw, ms=ms,
                label=f"{order}st order" if order==1 else f"{order}nd order" if order==2 else "3rd order")

    # ---------------------------------------------------------------------
    # reference slopes
    # ---------------------------------------------------------------------
    ref_x = np.array([50, 130])  # short horizontal range
    ref_y_levels = [1e-1, 1e-3, 1e-5]

    for order, y0 in zip([1, 2, 3], ref_y_levels):
        ref_y = y0 * (ref_x / ref_x[0]) ** (-order)
        plt.plot(ref_x, ref_y, '--', color='gray', lw=1.5, alpha=0.7)
        plt.text(ref_x[0] * 1.6, ref_y[0], f"$N^{{-{order}}}$",
                fontsize=11, color='gray', rotation=0)

    # ---------------------------------------------------------------------
    plt.xscale("log"); plt.yscale("log")
    plt.xlabel(r"Nodes $N$", fontsize=13)
    plt.ylabel(r"$L_{\infty}$ error", fontsize=13)
    plt.xticks(fontsize=11); plt.yticks(fontsize=11)
    plt.legend(fontsize=11, frameon=True, loc="lower left", framealpha=0.9)
    plt.grid()
    plt.tight_layout()
    plt.show()
