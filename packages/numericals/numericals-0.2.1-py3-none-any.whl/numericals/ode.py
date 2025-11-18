from collections.abc import Callable


def euler(
    function: Callable[[float], float], alpha: float, beta: float, y0: float, n: int
) -> list:
    """Solve ODE using Euler's Method.

    Parameters
    ----------
    function : Callable
        The function.
    alpha : float
        The lower limit.
    beta : float
        The upper limit.
    y0 : float
        The initial value.
    n : int
        The number of partitions.

    Returns
    -------
    list
        A function approximation (via a table).
    """
    values = []
    h = (beta - alpha) / n
    x = alpha
    y = y0
    values.append((x, y))

    for i in range(n):
        y = y + h * function(x, y)
        x = x + h
        values.append((x, y))

    return values
