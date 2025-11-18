from collections.abc import Callable


def bisection(
    function: Callable[[float], float],
    alpha: float,
    beta: float,
    tolerance: float = 1e-10,
    max_iterations: int = 10_000,
) -> float:
    """Find root using the Bisection Method.

    Parameters
    ----------
    function : Callable
        The function.
    alpha : float
        The lower bound.
    beta : float
        The upper bound.
    tolerance : float
        The tolerance.
    max_iterations : int
        The maximum number of iterations.

    Returns
    -------
    float
        A root approximation.
    """
    if function(alpha) == 0:
        return alpha
    if function(beta) == 0:
        return beta
    if function(alpha) * function(beta) > 0:
        raise ValueError

    for _ in range(max_iterations):
        midpoint = (alpha + beta) * 0.5
        fm = function(midpoint)
        if (abs(beta - alpha) * 0.5 < tolerance) or (fm == 0):
            return midpoint
        if fm * function(alpha) < 0:
            beta = midpoint
        else:
            alpha = midpoint

    return (alpha + beta) * 0.5


def secant(
    function: Callable[[float], float],
    x0: float,
    x1: float,
    tolerance: float = 1e-10,
    max_iterations: int = 10_000,
) -> float:
    """Find root using the Secant Method.

    Parameters
    ---------
    function : Callable
        The function.
    x0 : float
        The first initial guess.
    x1 : float
        The second initial guess.
    tolerance : float
        The tolerance.
    max_iterations : int
        The maximum number of iterations.

    Returns
    -------
    float
        A root approximation.
    """
    for _ in range(max_iterations):
        x2 = x1 - function(x1) * (x1 - x0) / (function(x1) - function(x0))

        x0 = x1
        x1 = x2

        if abs(x0 - x1) < tolerance:
            return x2

    return x2
