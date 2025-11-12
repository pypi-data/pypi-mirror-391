"""Utility module for molecularprofiles."""

from bisect import bisect_left

from scipy.interpolate import interp1d


def take_closest(my_list: list[float], my_number: float) -> float:
    """
    Return closest value to my_number.

    If two numbers are equally close, return the smallest number.
    This function comes from the answer of user:
    https://stackoverflow.com/users/566644/lauritz-v-thaulow
    found in stack overflow post:
    https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value/12141511#12141511

    Returns
    -------
    float
    """
    pos = bisect_left(my_list, my_number)
    if pos == 0:
        return my_list[0]
    if pos == len(my_list):
        return my_list[-1]
    before = my_list[pos - 1]
    after = my_list[pos]
    if after - my_number < my_number - before:
        return after
    return before


def interpolate(x_param, y_param, new_x_param, kind="cubic"):
    """
    Interpolates y-values at specified x-coordinates using given x and y data points.

    Parameters
    ----------
    x_param : array_like
        The x-coordinates of the data points.
    y_param : array_like
        The y-coordinates of the data points, corresponding to `x_param`.
    new_x_param : array_like
        The x-coordinates at which to evaluate the interpolated values.
    kind : str, optional
        Specifies the kind of interpolation as a string. Supported values are
        "linear", "nearest", "zero", "slinear", "quadratic", "cubic", etc.
        Default is "cubic".

    Returns
    -------
    numpy.ndarray
        The interpolated y-values at `new_x_param`.
    """
    func = interp1d(x_param, y_param, kind=kind, bounds_error=False)
    return func(new_x_param)
