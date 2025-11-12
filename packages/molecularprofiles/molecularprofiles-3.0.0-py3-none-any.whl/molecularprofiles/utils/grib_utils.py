"""Set of utilities for decoding and analysing grib files."""

import glob
import logging
import logging.config
import os

import astropy.units as u
import numpy as np
import pygrib as pg
from astropy.coordinates import Angle, Latitude, Longitude
from astropy.table import Table, join, vstack
from astropy.time import Time

from molecularprofiles.utils.constants import (
    DENSITY_SCALE_HEIGHT,
    STD_AIR_PRESSURE,
    STD_AIR_TEMPERATURE,
    STD_EARTH_RADIUS,
    STD_GRAVITATIONAL_ACCELERATION,
    STD_NUMBER_DENSITY,
)

ROOTDIR = os.path.dirname(os.path.abspath(__file__))
log_config_file = f"{ROOTDIR}/logger.conf"
logging.config.fileConfig(fname=log_config_file, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def get_altitude_from_geopotential_height(geopotential_height, latitude):
    """
    Compute the real altitude from the geopotential value.

    Uses expression 20 from http://dx.doi.org/10.1029/2002JB002333

    Parameters
    ----------
    geopotential : astropy.units.Quantity [u.m]
        Geopotential height
    latitude : astropy.coordinates.Latitude
        Geographical latitude of interest.

    Returns
    -------
    astropy.units.Quantity [u.m]
        Real altitude as fGeoidOffset.
    """
    lat = (np.asarray(latitude) * latitude.unit).to_value(u.rad)
    return (
        (1.0 + 0.002644 * np.cos(2 * lat)) * (geopotential_height)
        + (1 + 0.0089 * np.cos(2 * lat))
        * ((geopotential_height) ** 2 / STD_EARTH_RADIUS.to(u.m))
    ).to(u.m)


def get_gribfile_variables(filename):
    """
    Return all the different variable names in a grib file.

    Parameters
    ----------
    filename : str
       Path to the grib file.

    Returns
    -------
    list
        varname (str): variable names.
    list
        varshortname (str): variable short names.
    """
    logger.debug("Opening %s grib file", filename)
    with pg.open(filename) as grib_file:
        varshortname = []
        varname = []
        for message in grib_file:
            variable_name = message.name.replace(" ", "")
            variable_short_name = message.shortName
            if variable_name not in varname:
                varname.append(variable_name)
                varshortname.append(variable_short_name)
    return varname, varshortname


def create_table(grib_var):
    """
    Create astropy.table.Table from grib record.

    Parameters
    ----------
    grib_var :
        Grib data record

    Returns
    -------
     astropy.table.Table
         Table with the different measurables together with their dimensions
    """
    tables = []
    for v in grib_var:
        unit = u.Unit(v.units)
        timestamp = Time(
            {"year": v.year, "month": v.month, "day": v.day, "hour": v.hour},
            scale="utc",
        )
        pressure_level = v.level * u.hPa
        latitudes = Latitude(v.latlons()[0].ravel() * u.deg)
        longitudes = Longitude(v.latlons()[1].ravel() * u.deg, wrap_angle=180 * u.deg)
        if isinstance(v.values, float):
            vals = np.array([v.values]) * unit
        else:
            vals = v.values.ravel() * unit
        t = Table([latitudes, longitudes], names=["Latitude", "Longitude"])
        t["Timestamp"] = timestamp
        t["Pressure"] = pressure_level
        t[v.name] = vals
        tables.append(t)
    res = Table(vstack(tables), masked=True)
    del tables
    return res


def get_grib_file_data(filename):
    """
    Create astropy table with the data from a grib file.

    This function opens a grib file, selects the parameters
    (e.g., Temperature, Geopotential, RH, etc.),
    and creates an astropy.table.Table with them.

    Parameters
    ----------
    filename : str
        Path to the grib file.

    Returns
    -------
    astropy.table.Table
        Table with grib file data including isobaric and single level parameters.
    """
    _, variable_short_names = get_gribfile_variables(filename)
    grib_file = pg.open(filename)

    gpm = u.def_unit("gpm", u.m)
    u.add_enabled_units([gpm])

    data = Table()

    for short_name in variable_short_names:
        if short_name == "unknown":
            continue

        try:
            # First, try pressure levels
            var = grib_file.select(shortName=short_name, typeOfLevel="isobaricInhPa")
        except (ValueError, KeyError):
            try:
                # Try again without typeOfLevel
                var = grib_file.select(shortName=short_name)
            except (ValueError, KeyError):
                logger.debug("Variable %s not found in file", short_name)
                continue

        try:
            t = create_table(var)
        except ValueError:
            logger.warning("Grib message for %s can't be parsed", short_name)
            continue

        if len(data) == 0:
            data = t
        else:
            data = join(data, t, join_type="outer")

    return data


def extend_grib_data(data):
    """
    Extend grib data table.

    Extends grib data table by filling the gaps in data
    and calculating additional quantities:
    - altitude
    - density
    - exponential density
    - wind direction

    Parameters
    ----------
    astropy.table.Table
        Table with grib data

    Returns
    -------
    astropy.table.Table
        Extended table with grib data and additional quantities
    """
    logger.debug("Check for gaps in relative humidity and fill them if necessary")
    data["Relative humidity"] = data["Relative humidity"].filled(0)
    logger.debug("Compute altitude from geopotential")
    if "Geopotential height" in data.keys():
        data["Altitude"] = get_altitude_from_geopotential_height(
            data["Geopotential height"], data["Latitude"]
        )
    else:
        data["Altitude"] = get_altitude_from_geopotential_height(
            data["Geopotential"].quantity / STD_GRAVITATIONAL_ACCELERATION,
            data["Latitude"],
        )
    if "Ozone mixing ratio" in data.keys():
        data["Ozone mass mixing ratio"] = data["Ozone mixing ratio"].filled(0)
    elif "Ozone mass mixing ratio (full chemistry scheme)" in data.keys():
        data["Ozone mass mixing ratio"] = data[
            "Ozone mass mixing ratio (full chemistry scheme)"
        ].filled(0)
    logger.debug("Compute density")
    data["Density"] = (
        STD_NUMBER_DENSITY
        * data["Pressure"]
        / STD_AIR_PRESSURE
        * STD_AIR_TEMPERATURE
        / data["Temperature"]
    )
    logger.debug("Compute exponential density")
    data["Exponential Density"] = (
        data["Density"]
        / STD_NUMBER_DENSITY
        * np.exp(data["Altitude"] / DENSITY_SCALE_HEIGHT)
    )
    logger.debug("Compute wind speed")
    data["Wind Speed"] = np.sqrt(
        data["U component of wind"] ** 2 + data["V component of wind"] ** 2
    )
    logger.debug("Compute wind direction")
    data["Wind Direction"] = Angle(
        np.array(
            np.arctan2(
                -data["V component of wind"].value, -data["U component of wind"].value
            )
        ),
        unit=u.rad,
    ).wrap_at(360 * u.deg)
    return data


def save_grib_table(data, filename, fmt="ecsv"):
    """
    Save grib data in a file according to provided format.

    Parameters
    ----------
    data: astropy.table.Table
        Grib data in astropy table
    filename: str
        Path to the file
    fmt: str
        Desired format
    """
    if fmt == "ecsv":
        data.write(filename, format="ascii.ecsv", overwrite=True)
    elif fmt == "magic":
        raise NotImplementedError("Magic txt format writing is not implemented yet")
    else:
        raise ValueError("Not recognized format")


def convert_to_text(data_path):
    """
    Convert GRIB/GRIB2 files to ecsv.

    Parameters
    ----------
    data_path: path-like
        Path to the folder with GRIB/GRIB2 data files
    """
    grib_file_list = list(glob.glob(os.path.join(data_path, "*.grib2"))) + list(
        glob.glob(os.path.join(data_path, "*.grib"))
    )
    for grib_file in grib_file_list:
        data = get_grib_file_data(grib_file)
        data = extend_grib_data(data)
        save_grib_table(data, os.path.splitext(grib_file)[0] + ".ecsv")


def merge_ecsv_files(data_path):
    """
    Merge ecsv files.

    Parameters
    ----------
    data_path: path-like
        Path to the folder with GRIB/GRIB2 data files
    """
    tables = []
    for tfile in os.listdir(data_path):
        if tfile.endswith(".ecsv"):
            tables.append(Table.read(f"{data_path}/{tfile}"))
    merged_data = vstack(tables)
    del tables
    save_grib_table(merged_data, f"{data_path}/merged_file.ecsv")
