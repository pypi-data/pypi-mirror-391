import os
from importlib.resources import files

import astropy.units as u
import numpy as np
import pytest
from astropy.table import Table
from molecularprofiles.molecularprofiles import MolecularProfile
from molecularprofiles.tests import test_data
from molecularprofiles.utils import absorbing_molecules
from molecularprofiles.utils.constants import (
    MOLAR_MASS_NITROGEN_DIOXIDE,
    MOLAR_MASS_OZONE,
    STD_CORSIKA_ALTITUDE_PROFILE,
)
from molecularprofiles.utils.profiles_utils import (
    combine_extinction_profiles,
)

# Define Rayleigh scattering altitude bins
RAYLEIGH_SCATTERING_ALTITUDE_BINS = (
    2.158,
    2.208,
    2.258,
    2.358,
    2.458,
    2.658,
    2.858,
    3.158,
    3.658,
    4.158,
    4.5,
    5.0,
    5.5,
    6.0,
    7.0,
    8.0,
    9.0,
    10.0,
    11.0,
    12.0,
    13.0,
    14.0,
    15.0,
    16.0,
    18.0,
    20.0,
    22.0,
    24.0,
    26.0,
    28.0,
    30.0,
    32.5,
    35.0,
    37.5,
    40.0,
    45.0,
    50.0,
    55.0,
    60.0,
    65.0,
    70.0,
    75.0,
    80.0,
    85.0,
    90.0,
    95.0,
    100.0,
    105.0,
    110.0,
    115.0,
    120.0,
) * u.km


@pytest.fixture()
def empty_mol_profile():
    # Define the path to the test grib file
    grib_file_path = files(test_data).joinpath("grib/sample.grib")
    # Create and return the MolecularProfile instance
    return MolecularProfile(
        grib_file_path,
        stat_columns=(
            "Pressure",
            "Altitude",
            "Density",
            "Temperature",
            "Wind Speed",
            "Wind Direction",
            "Relative humidity",
            "Exponential Density",
            "Ozone mass mixing ratio",
        ),
    )


@pytest.fixture()
def mol_profile(empty_mol_profile):
    empty_mol_profile.get_data()
    return empty_mol_profile


def test_get_data(empty_mol_profile):
    # Test get_data method
    empty_mol_profile.get_data()
    # Perform assertions
    assert empty_mol_profile.data is not None
    assert empty_mol_profile.stat_data is not None
    assert empty_mol_profile.stat_description is not None
    assert isinstance(empty_mol_profile.data, Table)
    t_mol_profile = MolecularProfile("/foo/bar/baz.grib")
    with pytest.raises(FileNotFoundError):
        t_mol_profile.get_data()


def test_create_atmospheric_profile(mol_profile):
    # Define test parameters
    outfile = "test_atmospheric_profile.ecsv"
    outfile_bad = "test_atmospheric_profile.txt"
    co2_concentration = 415  # Placeholder value
    reference_atmosphere = None  # Placeholder value
    # Test create_atmospheric_profile method
    with pytest.raises(SystemExit):
        mol_profile.create_atmospheric_profile(
            co2_concentration, outfile_bad, reference_atmosphere
        )
    with pytest.raises(SystemExit):
        mol_profile.create_atmospheric_profile(
            co2_concentration,
            outfile,
            "path/to/nonexistent/reference/atmosphere/file.ecsv",
        )

    atmo_profile_table = mol_profile.create_atmospheric_profile(
        co2_concentration, outfile, reference_atmosphere
    )
    # Perform assertions
    assert os.path.isfile(outfile)
    assert isinstance(atmo_profile_table, Table)
    os.remove(outfile)
    reference_atmosphere_file_path = files(test_data).joinpath(
        "reference_atmospheres_tests/reference_atmo_model_v0_CTA-south_winter.ecsv"
    )
    reference_atmosphere = Table.read(
        reference_atmosphere_file_path, format="ascii.ecsv"
    )
    atmo_profile_table = mol_profile.create_atmospheric_profile(
        co2_concentration, outfile=None, reference_atmosphere=reference_atmosphere
    )
    assert isinstance(atmo_profile_table, Table)


def test_create_molecular_density_profile(mol_profile):
    # Define test parameters
    mdp_file = "test_mdp_file.ecsv"
    # Test create_molecular_density_profile method
    mdp_table = mol_profile.create_molecular_density_profile(mdp_file)
    # Perform assertions
    assert os.path.isfile(mdp_file)
    assert isinstance(mdp_table, Table)
    os.remove(mdp_file)


def test_create_rayleigh_extinction_profile(mol_profile):
    # Define test parameters
    rayleigh_extinction_file = "test_rayleigh_extinction_file.ecsv"
    co2_concentration = 415  # Placeholder value
    wavelength_min = u.Quantity(340, unit="nm")  # Placeholder value
    wavelength_max = u.Quantity(360, unit="nm")  # Placeholder value
    # Test rayleigh_extinction method
    rayleigh_extinction_table = mol_profile.create_rayleigh_extinction_profile(
        co2_concentration,
        wavelength_min,
        wavelength_max,
        rayleigh_extinction_file,
    )
    # Perform assertions
    assert os.path.isfile(rayleigh_extinction_file)
    assert isinstance(rayleigh_extinction_table, Table)
    os.remove(rayleigh_extinction_file)


def test_timeseries_analysis_altitude(mol_profile):
    # Define test parameters
    outfile = "test_timeseries_analysis_alt.ecsv"
    parameter_level = u.Quantity(2200, unit="m")
    atmospheric_parameter = "Temperature"
    interpolation_parameter = "Altitude"
    t_floor = u.Quantity(1000, unit="m")
    t_ceiling = u.Quantity(20000, unit="m")
    # Test timeseries_analysis method
    mol_profile.timeseries_analysis(
        outfile,
        parameter_level,
        atmospheric_parameter,
        interpolation_parameter,
        m_floor=t_floor,
        m_ceiling=t_ceiling,
        interpolation_list=STD_CORSIKA_ALTITUDE_PROFILE,
    )
    # Perform assertions
    assert os.path.isfile(outfile)
    os.remove(outfile)


def test_timeseries_analysis_pressure(mol_profile):
    # Define test parameters
    outfile = "test_timeseries_analysis_p.ecsv"
    parameter_level = u.Quantity(750, unit="hPa")
    atmospheric_parameter = "Temperature"
    interpolation_parameter = "Pressure"
    t_floor = u.Quantity(500, unit="hPa")
    t_ceiling = u.Quantity(1000, unit="hPa")
    interpolation_list = (1000, 900, 800, 700, 600, 500) * u.hPa
    # Test timeseries_analysis method
    mol_profile.timeseries_analysis(
        outfile,
        parameter_level,
        atmospheric_parameter,
        interpolation_parameter,
        m_floor=t_floor,
        m_ceiling=t_ceiling,
        interpolation_list=interpolation_list,
    )
    # Perform assertions
    assert os.path.isfile(outfile)
    os.remove(outfile)


def test_combine_extinction_profiles(mol_profile):
    # Define test parameters
    mep_file = "molecular_extinction_file.ecsv"
    reference_atmosphere_file_path = files(test_data).joinpath(
        "reference_atmospheres_tests/reference_atmo_model_v0_CTA-south_winter.ecsv"
    )
    molecule_name = "Ozone"
    ozone_cross_section_file = files(absorbing_molecules).joinpath(
        "ozone_cross_section_293K.ecsv"
    )
    co2_concentration = 415  # Placeholder value
    wavelength_min = u.Quantity(340, unit="nm")  # Placeholder value
    wavelength_max = u.Quantity(360, unit="nm")  # Placeholder value
    rayleigh_extinction_table = mol_profile.create_rayleigh_extinction_profile(
        co2_concentration,
        wavelength_min,
        wavelength_max,
        reference_atmosphere=reference_atmosphere_file_path,
        rayleigh_scattering_altitude_bins=RAYLEIGH_SCATTERING_ALTITUDE_BINS,
    )
    ozone_absorption_table = mol_profile.create_molecular_absorption_profile(
        molecule_name,
        ozone_cross_section_file,
        wavelength_min,
        wavelength_max,
        MOLAR_MASS_OZONE,
        altitude_bins=RAYLEIGH_SCATTERING_ALTITUDE_BINS,
    )
    molecular_extinction_table = combine_extinction_profiles(
        rayleigh_extinction_table, ozone_absorption_table, mep_file
    )
    assert os.path.isfile(mep_file)
    assert isinstance(molecular_extinction_table, Table)
    os.remove(mep_file)


def test_nitrogen_dioxide_absorption():
    # Define test parameter
    molecule_name = "Nitrogen dioxide"
    stat_columns = (
        "Pressure",
        "Altitude",
        "Density",
        "Temperature",
        "Wind Speed",
        "Wind Direction",
        "Relative humidity",
        "Exponential Density",
        "Ozone mass mixing ratio",
        "Nitrogen dioxide mass mixing ratio",
        "Nitrogen monoxide mass mixing ratio",
    )
    nitrogen_dioxide_file_path = files(test_data).joinpath(
        "absorbing_molecules_tests/sample_cams_molecules.grib"
    )
    no2_molecular_profile = MolecularProfile(nitrogen_dioxide_file_path, stat_columns)
    no2_molecular_profile.get_data()
    no2_cross_section_file = files(absorbing_molecules).joinpath(
        "nitrogen_dioxide_absorption_cross_section_294K.ecsv"
    )
    wavelength_min = u.Quantity(340, unit="nm")  # Placeholder value
    wavelength_max = u.Quantity(360, unit="nm")  # Placeholder value
    no2_absorption_table = no2_molecular_profile.create_molecular_absorption_profile(
        molecule_name,
        no2_cross_section_file,
        wavelength_min,
        wavelength_max,
        MOLAR_MASS_NITROGEN_DIOXIDE,
        altitude_bins=RAYLEIGH_SCATTERING_ALTITUDE_BINS,
    )
    assert isinstance(no2_absorption_table, Table)


def test_molecular_absorption_combination():
    # Define test parameter
    stat_columns = (
        "Pressure",
        "Altitude",
        "Density",
        "Temperature",
        "Wind Speed",
        "Wind Direction",
        "Relative humidity",
        "Exponential Density",
        "Ozone mass mixing ratio",
        "Nitrogen dioxide mass mixing ratio",
        "Nitrogen monoxide mass mixing ratio",
    )
    nitrogen_dioxide_file_path = files(test_data).joinpath(
        "absorbing_molecules_tests/sample_cams_molecules.grib"
    )
    no2_ozone_molecular_profile = MolecularProfile(
        nitrogen_dioxide_file_path, stat_columns
    )
    no2_ozone_molecular_profile.get_data()
    molecule_names = ["Ozone", "Nitrogen dioxide"]
    cross_section_files = [
        files(absorbing_molecules).joinpath("ozone_cross_section_293K.ecsv"),
        files(absorbing_molecules).joinpath(
            "nitrogen_dioxide_absorption_cross_section_294K.ecsv"
        ),
    ]
    wavelength_min = u.Quantity(340, unit="nm")  # Placeholder value
    wavelength_max = u.Quantity(360, unit="nm")  # Placeholder value
    molecule_absorption_tables = [
        no2_ozone_molecular_profile.create_molecular_absorption_profile(
            molecule_name,
            cross_section_file,
            wavelength_min,
            wavelength_max,
            (
                MOLAR_MASS_OZONE
                if molecule_name == "Ozone"
                else MOLAR_MASS_NITROGEN_DIOXIDE
            ),
            altitude_bins=RAYLEIGH_SCATTERING_ALTITUDE_BINS,
        )
        for molecule_name, cross_section_file in zip(
            molecule_names, cross_section_files
        )
    ]
    combined_molecular_absorption_table = combine_extinction_profiles(
        *molecule_absorption_tables
    )
    assert isinstance(combined_molecular_absorption_table, Table)


def test_stat_analysis(mol_profile):
    outfile = "test_timeseries_analysis.ecsv"
    altitudes = np.array([1, 3, 7]) * u.km

    mol_profile.stat_analysis("Temperature", altitudes, outfile)

    assert os.path.isfile(outfile)

    table = Table.read(outfile)

    expected_cols = [
        "altitude",
        "atmo_param",
        "atmo_param_std",
        "atmo_param_p2p_max",
        "atmo_param_p2p_min",
    ]
    assert table.colnames == expected_cols
