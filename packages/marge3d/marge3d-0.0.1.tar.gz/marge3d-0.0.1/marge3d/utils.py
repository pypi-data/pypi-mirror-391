import numpy as np

def numerical_order(n_steps, err):
    """
    Compute numerical order from two vectors containing the error and the number of time-steps.

    Parameters
    ----------
    n_steps : np.1darray or list
        Different number of steps to compute the error.
    err : np.1darray
        Different error values associated to the number of steps.

    Returns
    -------
    beta : float
        Order coefficient computed through linear regression.
    rmse : float
        The root mean square error of the linear regression.
    """
    n_steps = np.asarray(n_steps)
    x, y = np.log10(1/n_steps), np.log10(err)

    # Compute regression coefficients and rmse
    xMean = x.mean()
    yMean = y.mean()
    sX = ((x-xMean)**2).sum()
    sXY = ((x-xMean)*(y-yMean)).sum()

    beta = sXY/sX
    alpha = yMean - beta*xMean

    yHat = alpha + beta*x
    rmse = ((y-yHat)**2).sum()**0.5
    rmse /= x.size**0.5

    return beta, rmse