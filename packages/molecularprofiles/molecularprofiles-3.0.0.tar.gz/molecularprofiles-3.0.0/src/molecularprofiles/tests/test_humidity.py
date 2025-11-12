import astropy.units as u
import numpy as np
from molecularprofiles.utils.humidity import (
    compressibility,
    density_moist_air,
    enhancement_factor,
    molar_fraction_water_vapor,
    partial_pressure_water_vapor,
    saturation_vapor_pressure,
    saturation_vapor_pressure_over_ice,
    saturation_vapor_pressure_over_water,
)

# Sample data for tests
co2_bkg = 400  # ppmv
pressure = 1013.25 * u.hPa
temperature = 293.15 * u.K
relative_humidity = 50 * u.percent
expected_compressibility = 0.99962
expected_enhancement_factor = 1.00403
expected_saturation_vapor_pressure = 2339.16323 * u.Pa
expected_saturation_vapor_pressure_over_water = 2339.21477 * u.Pa
expected_molar_fraction_water_vapor = 0.0115893
expected_density_moist_air = 1.19922 * u.kg / u.m**3
expected_partial_pressure_water_vapor = 1169.58162 * u.Pa
expected_saturation_vapor_pressure_over_ice = 2832.32948 * u.Pa


def test_compressibility():
    # Test the function with sample data
    z = compressibility(pressure, temperature, expected_molar_fraction_water_vapor)

    # Perform assertions
    assert np.isclose(z, expected_compressibility)


def test_enhancement_factor():
    # Test the function with sample data
    f = enhancement_factor(pressure, temperature)

    # Perform assertions
    assert np.isclose(f, expected_enhancement_factor)


def test_saturation_vapor_pressure():
    # Test the function with sample data
    psv = saturation_vapor_pressure(temperature)

    # Perform assertions
    assert np.isclose(psv, expected_saturation_vapor_pressure)


def test_saturation_vapor_pressure_over_water():
    # Test the function with sample data
    psv_over_water = saturation_vapor_pressure_over_water(temperature)

    # Perform assertions
    assert np.isclose(psv_over_water, expected_saturation_vapor_pressure_over_water)


def test_saturation_vapor_pressure_over_ice():
    # Test the function with sample data
    psv_over_ice = saturation_vapor_pressure_over_ice(temperature)

    # Perform assertions
    assert np.isclose(psv_over_ice, expected_saturation_vapor_pressure_over_ice)


def test_molar_fraction_water_vapor():
    # Test the function with sample data
    x_w = molar_fraction_water_vapor(pressure, temperature, relative_humidity)

    # Perform assertions
    assert np.isclose(x_w, expected_molar_fraction_water_vapor)


def test_density_moist_air():
    # Test the function with sample data
    rho = density_moist_air(
        pressure,
        temperature,
        expected_compressibility,
        expected_molar_fraction_water_vapor,
        co2_bkg,
    )

    # Perform assertions
    assert np.isclose(rho, expected_density_moist_air)


def test_partial_pressure_water_vapor():
    # Test the function with sample data
    p_wv = partial_pressure_water_vapor(temperature, relative_humidity)

    # Perform assertions
    assert np.isclose(p_wv, expected_partial_pressure_water_vapor)
