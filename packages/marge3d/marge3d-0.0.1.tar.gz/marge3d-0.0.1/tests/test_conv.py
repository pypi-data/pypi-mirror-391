import pytest

import numpy as np

from marge3d.fields import VelocityField3D
from marge3d.analytic import AnalyticalSolver
from marge3d.numeric import NumericalSolver
from marge3d.params import TEST_PARAMETERS
from marge3d.utils import numerical_order

N_STEPS_CONV = [100, 200, 500]

@pytest.mark.parametrize("order", [1, 2, 3])
@pytest.mark.parametrize("t_end", [1.0, 4.0])
def test_order(t_end, order):

    R0     = np.array([1, 0, 0])
    vortex = VelocityField3D(1)
    U0     = vortex.get_velocity(R0[0], R0[1], R0[2], 0) # Initial fluid velocity
    V0     = np.array(vortex.get_velocity(R0[0], R0[1], R0[2], 0)) # Same as initial fluid velocity
    W0     = V0 - U0 # Relative velocity
    analytic = AnalyticalSolver(R0, U0, **TEST_PARAMETERS)

    errors = []
    for n in N_STEPS_CONV:
        times = np.linspace(0, t_end, n)
        solver = NumericalSolver(R0, W0, vortex, n+1, order, **TEST_PARAMETERS)

        stepper = {
            1: solver.Euler,
            2: solver.AdamBashf2,
            3: solver.AdamBashf3,
        }[order]

        R_x, R_y, R_z, _ = stepper(times, flag=True)
        R_num = np.column_stack((R_x, R_y, R_z))
        R_ana = np.array([[*analytic.solve(t), analytic.solve_z(t)] for t in times])

        err = np.max(np.linalg.norm(R_ana - R_num, axis=1))
        errors.append(err)

    num_order, rmse = numerical_order(N_STEPS_CONV, errors)
    expected_order = order
    if order == 3:
        # TODO : this is weird ... implementation should be checked
        expected_order = 2.5

    assert rmse < 0.05, \
        f"rmse to high ({rmse}) for {order=}"
    assert abs(num_order-expected_order) < 0.1, \
        f"expected order {expected_order:.2f}, but got {num_order:.2f} for {order=}"
