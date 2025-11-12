import astropy.units as u
import numpy as np
import pytest
from molecularprofiles.utils.rayleigh import (
    Rayleigh,
)


@pytest.fixture()
def rayleigh_instance():
    wavelength = 500 * u.nm
    co2_bkg = 400  # ppmv
    pressure = 1013.25 * u.hPa
    temperature = 288 * u.K
    relative_humidity = 50 * u.percent

    return Rayleigh(
        wavelength=wavelength,
        co2_bkg=co2_bkg,
        pressure=pressure,
        temperature=temperature,
        relative_humidity=relative_humidity,
    )


# Define expected values for expected quantities
expected_molecular_number_density = 2.548225509895833e19 / u.cm**3
expected_scattering_cross_section = 6.644048956193942e-27 * u.cm**2
expected_beta = 0.0169305 / u.km
expected_refractive_index = 1.0002788
expected_king_factor = 1.04895
expected_depolarization = 0.0283975
expected_angle = (
    45 * u.deg
)  # Default angle for testing phase function and back scattering coefficient
expected_phase = 1.11975
expected_back_scattering_coefficient = 0.00150863 / u.km


@pytest.mark.parametrize("wavelength", [199 * u.nm, 4001 * u.nm])
def test_wavelength_boundary(wavelength):
    with pytest.raises(
        ValueError, match="Wavelength range only from 200 nm - 4 micrometer allowed."
    ):
        Rayleigh(wavelength=wavelength, co2_bkg=400)


@pytest.mark.parametrize("pressure", [-1 * u.hPa, 1401 * u.hPa])
def test_pressure_boundary(pressure):
    with pytest.raises(
        ValueError, match="Pressure only in range 0 - 1400 hPa allowed."
    ):
        Rayleigh(wavelength=500 * u.nm, co2_bkg=400, pressure=pressure)


@pytest.mark.parametrize("temperature", [149 * u.K, 401 * u.K])
def test_temperature_boundary(temperature):
    with pytest.raises(
        ValueError, match="Temperatures only in range 150 - 400 K allowed."
    ):
        Rayleigh(wavelength=500 * u.nm, co2_bkg=400, temperature=temperature)


@pytest.mark.parametrize("co2_bkg", [199, 1001])
def test_co2_bkg_boundary(co2_bkg):
    with pytest.raises(
        ValueError, match="CO2 concentrations only in range 200 - 1000 ppmv allowed."
    ):
        Rayleigh(wavelength=500 * u.nm, co2_bkg=co2_bkg)


def test_molecular_number_density(rayleigh_instance):
    # Test calculation of molecular number density
    assert np.isclose(
        rayleigh_instance.molecular_number_density.value,
        expected_molecular_number_density.value,
    )


def test_scattering_cross_section(rayleigh_instance):
    # Test calculation of scattering cross section
    assert np.isclose(
        rayleigh_instance.scattering_cross_section.value,
        expected_scattering_cross_section.value,
    )


def test_beta(rayleigh_instance):
    # Test calculation of beta
    assert np.isclose(rayleigh_instance.beta.value, expected_beta.value)


def test_refractive_index(rayleigh_instance):
    # Test calculation of refractive index
    assert np.isclose(rayleigh_instance.refractive_index, expected_refractive_index)


def test_king_factor(rayleigh_instance):
    # Test calculation of king factor
    assert np.isclose(rayleigh_instance.king_factor, expected_king_factor)


def test_depolarization(rayleigh_instance):
    # Test calculation of depolarization
    assert np.isclose(rayleigh_instance.depolarization, expected_depolarization)

    # Add more test cases for different inputs and edge cases


def test_phase_function(rayleigh_instance):
    # Test calculation of phase function
    assert np.isclose(rayleigh_instance.phase_function(expected_angle), expected_phase)


def test_back_scattering_coefficient(rayleigh_instance):
    # Test calculation of back scattering coefficient
    assert np.isclose(
        rayleigh_instance.back_scattering_coefficient(expected_angle).value,
        expected_back_scattering_coefficient.value,
    )
