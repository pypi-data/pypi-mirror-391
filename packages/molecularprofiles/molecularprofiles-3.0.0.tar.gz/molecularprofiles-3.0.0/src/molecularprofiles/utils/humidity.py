"""
Collection of routines for calculation of moist air properties.

Provides:

* density
* compressibility
* enhancement factor
* saturation vapor pressure
* molar fraction from relative humidity
* partial pressure from relative humidity

Adapted from MHumidity, written by Markus Gaug <markus.gaug@uab.cat>, 04/2013
"""

import astropy.units as u
import numpy as np

from molecularprofiles.utils.constants import GAS_CONSTANT, MOLAR_MASS_WATER_VAPOR


def compressibility(pressure, temperature, x_w):
    """
    Calculate the compressibility of moist air.

    Parameters
    ----------
    pressure : astropy.units.Quantity
        Atmospheric pressure
    temperature : astropy.units.Quantity
        Air temperature
    x_w : float
        Molar fraction of water vapor

    Returns
    -------
    float
        compressibility of moist air (dimensionless constant, 0 < Z < 1)

    Notes
    -----
    Implemented according to Eq. 5 of [1]_. Notation and constants according to
    Eq. 16 of [2]_.

    References
    ----------
    .. [1] R.S. Davis, "Equation for the determination of the density of moist air"
       Metrologia, 29 (1992) 67-70
    .. [2] C. Tomasi, V. Vitale, B. Petkov, A. Lupi, A. Cacciari "Improved algorithm
       for calculations of Rayleigh-scattering optical depth in standard atmospheres",
       Applied Optics 44 Nr. 16 (2005) 3320
    """
    p = pressure.to(u.Pa)
    T = temperature.to(u.K, equivalencies=u.temperature())
    a_0 = 1.58123e-6 * u.K / u.Pa
    a_1 = -2.9331e-8 / u.Pa
    a_2 = 1.1043e-10 / (u.K * u.Pa)
    b_0 = 5.707e-6 * u.K / u.Pa
    b_1 = -2.051e-8 / u.Pa
    c_0 = 1.9898e-4 * u.K / u.Pa
    c_1 = -2.376e-6 / u.Pa
    d_0 = 1.83e-11 * u.K**2 / u.Pa**2
    d_1 = -7.65e-9 * u.K**2 / u.Pa**2

    return (
        1
        - p
        / T
        * (
            a_0
            + a_1 * (T - 273.15 * u.K)
            + a_2 * (T - 273.15 * u.K) ** 2
            + (b_0 + b_1 * (T - 273.15 * u.K)) * x_w
            + (c_0 + c_1 * (T - 273.15 * u.K)) * x_w**2
        )
        + p**2 / T**2 * (d_0 + d_1 * x_w**2)
    ).to_value()


def enhancement_factor(pressure, temperature):
    """
    Calculate the enhancement factor of water vapor in air.

    Parameters
    ----------
    pressure : astropy.units.Quantity
        Atmospheric pressure
    temperature : astropy.units.Quantity
        Air temperature

    Returns
    -------
    float
        Enhancement factor (dimensionless constant)

    Notes
    -----
    Calculated according to Eq. 14 of [1]_.

    References
    ----------
    .. [1] C. Tomasi, V. Vitale, B. Petkov, A. Lupi, A. Cacciari "Improved algorithm
       for calculations of Rayleigh-scattering optical depth in standard atmospheres",
       Applied Optics 44 Nr. 16 (2005) 3320
    """
    p = pressure.to(u.Pa)
    T = temperature.to(u.K, equivalencies=u.temperature())
    return (
        1.00062 + 3.14e-8 * p / u.Pa + 5.6e-7 * (T - 273.15 * u.K) ** 2 / u.K**2
    ).to_value()


def saturation_vapor_pressure(temperature):
    """
    Calculate the vapor pressure at saturation.

    Parameters
    ----------
    temperature : astropy.units.Quantity
        Air temperature

    Returns
    -------
    astropy.units.Quantity
        Saturation vapor pressure

    Notes
    -----
    In case temperatures above 0 deg C it follows [1]_, see also Eq. 15 in [2]_.
    Otherwise, Goff-Gratch equation (Eq. 1 in [3]_) is used.

    References
    ----------
    .. [1] R.S. Davis, "Equation for the determination of the density of moist air"
       Metrologia, 29 (1992) 67-70
    .. [2] C. Tomasi, V. Vitale, B. Petkov, A. Lupi, A. Cacciari "Improved algorithm
       for calculations of Rayleigh-scattering optical depth in standard atmospheres",
       Applied Optics 44 Nr. 16 (2005) 3320
    .. [3] http://cires.colorado.edu/~voemel/vp.html
    """
    T = temperature.to(u.K, equivalencies=u.temperature())
    mask = T > 273.15 * u.K
    res = np.empty(T.shape)
    res[mask] = (
        np.exp(
            1.2378847e-5 / u.K**2 * T[mask] ** 2
            - 1.9121316e-2 / u.K * T[mask]
            + 33.93711047
            - 6343.1645 * u.K / T[mask]
        )
        / 100.0
        # * u.Pa
    )

    theta = (
        373.16 * u.K / T[~mask]
    ).to_value()  # ratio of steam point (100 deg C) to temperature
    res[~mask] = (
        np.power(
            10,
            (
                -7.90298 * (theta - 1)
                + 5.02808 * np.log10(theta)
                - 1.3816e-7 * (np.power(10, 11.344 * (1 - 1 / theta)) - 1)
                + 8.1328e-3 * (np.power(10, -3.49149 * (theta - 1)) - 1)
                + np.log10(1013.246)
            ),
        )
        # * u.hPa
    )

    return res * u.hPa


# pylint: disable=too-many-locals
def saturation_vapor_pressure_over_water(temperature):
    """
    Calculate the vapor pressure at saturation over water.

    Parameters
    ----------
    temperature : astropy.units.Quantity
        Air temperature

    Returns
    -------
    astropy.units.Quantity
        Saturation vapor pressure

    Notes
    -----
    Implemented according to [1]_. See also [2]_ and [3]_.

    References
    ----------
    .. [1] International Association for the Properties of Water and Steam,
       Peter H. Huang, "New equations for water vapor pressure in the temperature
       range -100 deg. C to 100 deg. C for use with the 1997 NIST/ASME steam tables"
       Papers and abstracts from the third international symposium on humidity and
       moisture, Vol. 1, p. 69-76, National Physical Laboratory, Teddington,
       Middlesex, UK, April 1998.
    .. [2] http://cires.colorado.edu/~voemel/vp.html
    .. [3] https://emtoolbox.nist.gov/wavelength/documentation.asp#AppendixA
    """
    T = temperature.to(u.K, equivalencies=u.temperature()).to_value()
    k_1 = 1.16705214528e03
    k_2 = -7.24213167032e05
    k_3 = -1.70738469401e01
    k_4 = 1.20208247025e04
    k_5 = -3.23255503223e06
    k_6 = 1.49151086135e01
    k_7 = -4.82326573616e03
    k_8 = 4.05113405421e05
    k_9 = -2.38555575678e-01
    k_10 = 6.50175348448e02

    omega = T + k_9 / (T - k_10)
    a = omega**2 + k_1 * omega + k_2
    b = k_3 * omega**2 + k_4 * omega + k_5
    c = k_6 * omega**2 + k_7 * omega + k_8
    x = -b + np.sqrt(b**2 - 4 * a * c)
    return 1e6 * np.power(2 * c / x, 4) * u.Pa


# pylint: enable=too-many-locals


def saturation_vapor_pressure_over_ice(temperature):
    """
    Calculate the vapor pressure at saturation over ice.

    Parameters
    ----------
    temperature: astropy.units.Quantity
        Air temperature

    Returns
    -------
    astropy.units.Quantity
        Saturation vapor pressure

    Notes
    -----
    Implemented according to [1]_. See also [2]_ and [3]_.

    References
    ----------
    .. [1] International Association for the Properties of Water and Steam,
       Peter H. Huang, "New equations for water vapor pressure in the temperature
       range -100 deg. C to 100 deg. C for use with the 1997 NIST/ASME steam tables"
       Papers and abstracts from the third international symposium on humidity and
       moisture, Vol. 1, p. 69-76, National Physical Laboratory, Teddington,
       Middlesex, UK, April 1998.
    .. [2] http://cires.colorado.edu/~voemel/vp.html
    .. [3] https://emtoolbox.nist.gov/wavelength/documentation.asp#AppendixA
    """
    theta = (
        temperature.to(u.K, equivalencies=u.temperature()) / 273.16 * u.K
    ).to_value()
    a_1 = -13.928169
    a_2 = 34.7078238
    y = a_1 * (1 - np.power(theta, -1.5)) + a_2 * (1 - np.power(theta, -1.25))
    return 611.657 * np.exp(y) * u.Pa


def molar_fraction_water_vapor(pressure, temperature, relative_humidity):
    """
    Calculate the molar fraction of water vapor in moist air.

    Parameters
    ----------
    pressure : astropy.units.Quantity
        Atmospheric pressure
    temperature : astropy.units.Quantity
        Air temperature
    relative_humidity : float
        Relative humidity in percent

    Returns
    -------
    float
        Molar fraction of water vapor in moist air (dimensionless)

    Notes
    -----
    See the text above Eq. 14 in [1]_.

    References
    ----------
    .. [1] C. Tomasi, V. Vitale, B. Petkov, A. Lupi, A. Cacciari
       "Improved algorithm for calculations of Rayleigh-scattering optical depth
       in standard atmospheres", Applied Optics 44 Nr. 16 (2005) 3320
    """
    factor = enhancement_factor(pressure, temperature)
    psv = saturation_vapor_pressure(temperature)
    return (
        factor
        * relative_humidity.to(u.dimensionless_unscaled)
        * (psv / pressure).decompose()
    ).to_value()


def density_moist_air(pressure, temperature, moist_air_compressibility, x_w, co2_bkg):
    """
    Calculate the density of moist air.

    Parameters
    ----------
    pressure : astropy.units.Quantity
        Atmospheric pressure
    temperature : astropy.units.Quantity
        Temperature
    moist_air_compressibility : float
        Compressibility (see compressibility() in this module)
    x_w : float
        Molar fraction of water vapor
    co2_bkg : float
        CO2 volume concentration in ppmv (different unit than in Davis!)

    Returns
    -------
    astropy.units.Quantity
        Density of moist air

    Notes
    -----
    Density equation of moist air, according to Eq. 1 of [1]_.

    References
    ----------
    .. [1] R.S. Davis, "Equation for the determination of the density of moist air"
       Metrologia, 29 (1992) 67-70
    """
    R = GAS_CONSTANT
    m_w = MOLAR_MASS_WATER_VAPOR
    m_a = (
        1e-3 * (28.9635 + 12.011e-6 * (co2_bkg - 400)) * u.kg / u.mol
    )  # molar mass of dry air [kg/mol]
    return (
        pressure.to(u.Pa)
        * m_a
        / (
            moist_air_compressibility
            * R
            * temperature.to(u.K, equivalencies=u.temperature())
        )
        * (1 - x_w * (1 - m_w / m_a))
    ).decompose()  # Tomasi eq. 12


def partial_pressure_water_vapor(temperature, relative_humidity):
    """
    Calculate the partial pressure of water vapor in the air.

    Parameters
    ----------
    temperature : astropy.units.Quantity
        Temperature
    relative_humidity : astropy.units.Quantity
        Relative humidity

    Returns
    -------
    astropy.units.Quantity
        Water vapor partial pressure
    """
    return relative_humidity.to(u.dimensionless_unscaled) * saturation_vapor_pressure(
        temperature
    )
