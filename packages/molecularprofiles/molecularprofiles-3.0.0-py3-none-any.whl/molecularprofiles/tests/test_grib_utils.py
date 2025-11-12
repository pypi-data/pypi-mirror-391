import os

import astropy.units as u
import numpy as np
import pygrib as pg
import pytest
from astropy.table import Table
from molecularprofiles.utils.grib_utils import (
    convert_to_text,
    create_table,
    extend_grib_data,
    get_altitude_from_geopotential_height,
    get_grib_file_data,
    get_gribfile_variables,
    merge_ecsv_files,
    save_grib_table,
)

# Sample data for tests
current_dir = os.path.dirname(os.path.abspath(__file__))
test_data_dir = os.path.join(current_dir, "test_data/grib")
geopotential_height = 3000.0 * u.m
latitude = 45.0 * u.deg
filename = "sample.grib"  # Example filename
expected_altitude = 3001.441153 * u.m
expected_varname = [
    "Geopotential",
    "Ozonemassmixingratio",
    "Potentialvorticity",
    "Relativehumidity",
    "Temperature",
    "Ucomponentofwind",
    "Vcomponentofwind",
    "Verticalvelocity",
    "Divergence",
]
expected_varshortname = ["z", "o3", "pv", "r", "t", "u", "v", "w", "d"]
expected_indices = [0, 1, 2]  # Expected indices
expected_length = 1036  # Expected data length
expected_columns = [
    "Latitude",
    "Longitude",
    "Timestamp",
    "Pressure",
    "Geopotential",
    "Ozone mass mixing ratio",
    "Potential vorticity",
    "Relative humidity",
    "Temperature",
    "U component of wind",
    "V component of wind",
    "Vertical velocity",
    "Divergence",
]
expected_pressure = np.array([1000, 900, 800])  # Expected pressure values


def test_get_altitude_from_geopotential_height():
    altitude = get_altitude_from_geopotential_height(geopotential_height, latitude)

    # Perform assertions
    assert np.isclose(altitude, expected_altitude)


def test_get_gribfile_variables():
    varname, varshortname = get_gribfile_variables(
        os.path.join(test_data_dir, filename)
    )

    # Perform assertions
    assert set(varname) == set(expected_varname)
    assert set(varshortname) == set(expected_varshortname)


def test_create_table():
    grib_file = pg.open(os.path.join(test_data_dir, filename))
    grib_var = grib_file.select(shortName="t", typeOfLevel="isobaricInhPa")
    table = create_table(grib_var)

    # Perform assertions
    assert len(table) == expected_length
    assert list(table.columns) == [
        "Latitude",
        "Longitude",
        "Timestamp",
        "Pressure",
        "Temperature",
    ]


def test_get_grib_file_data():
    data = get_grib_file_data(os.path.join(test_data_dir, filename))

    # Perform assertions
    assert len(data) == expected_length
    assert set(data.columns) == set(expected_columns)


def test_extend_grib_data():
    # Prepare input data
    data = get_grib_file_data(os.path.join(test_data_dir, filename))
    # Test the function with sample data
    extended_data = extend_grib_data(data)

    # Perform assertions
    assert len(extended_data) == len(data)
    assert "Altitude" in extended_data.columns
    assert "Density" in extended_data.columns
    assert "Exponential Density" in extended_data.columns
    assert "Wind Direction" in extended_data.columns
    assert "Wind Speed" in extended_data.columns


def test_save_grib_table(tmpdir="/tmp/"):
    # Prepare input data
    data = get_grib_file_data(os.path.join(test_data_dir, filename))
    output = f"{tmpdir}/test_output.ecsv"
    fmt = "ecsv"
    # Test the function with sample data
    save_grib_table(data, output, fmt=fmt)

    # Perform assertions
    assert os.path.isfile(output)

    with pytest.raises(ValueError, match="Not recognized format"):
        save_grib_table(data, output, fmt="txt")

    with pytest.raises(NotImplementedError):
        save_grib_table(data, output, fmt="magic")


def test_convert_to_text():
    # Test the function with sample data
    convert_to_text(test_data_dir)

    # Perform assertions
    for tfile in os.listdir(test_data_dir):
        if tfile.endswith(".grib") or tfile.endswith(".grib2"):
            assert os.path.isfile(
                os.path.join(test_data_dir, os.path.splitext(tfile)[0] + ".ecsv")
            )


def test_merge_ecsv_files(tmpdir):
    # Test the function with sample data
    merge_ecsv_files(test_data_dir)

    # Perform assertions
    assert os.path.isfile(f"{test_data_dir}/merged_file.ecsv")
    table = Table.read(f"{test_data_dir}/merged_file.ecsv")
    assert len(table) == 2 * expected_length
    assert sorted(table.columns) == sorted(
        expected_columns
        + ["Altitude", "Density", "Exponential Density", "Wind Direction", "Wind Speed"]
    )
    os.remove(f"{test_data_dir}/merged_file.ecsv")
