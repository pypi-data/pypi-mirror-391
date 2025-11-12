"""
Provides ``MolecularProfile`` class, a main entry point for meteorological data analysis.

The molecular absorption cross sections have been retrieved from the `HITRAN2020 database <https://doi.org/10.1016/j.jqsrt.2021.107949>`_.
"""

import logging
import os
import sys

import astropy.units as u
import numpy as np
from astropy.io.registry.base import IORegistryError
from astropy.table import Column, QTable, Table, vstack
from astropy.units import Quantity

from molecularprofiles.utils import interpolate, take_closest
from molecularprofiles.utils.constants import (
    DENSITY_SCALE_HEIGHT,
    MOLAR_MASS_OZONE,
    N0_AIR,
    N_A,
    RAYLEIGH_SCATTERING_ALTITUDE_BINS,
    STD_AIR_DENSITY,
    STD_CORSIKA_ALTITUDE_PROFILE,
    STD_GRAVITATIONAL_ACCELERATION,
)
from molecularprofiles.utils.grib_utils import extend_grib_data, get_grib_file_data
from molecularprofiles.utils.humidity import (
    compressibility,
    density_moist_air,
    molar_fraction_water_vapor,
    partial_pressure_water_vapor,
)
from molecularprofiles.utils.rayleigh import Rayleigh

ROOTDIR = os.path.dirname(os.path.abspath(__file__))
log_config_file = f"{ROOTDIR}/utils/logger.conf"
logging.config.fileConfig(fname=log_config_file, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def _write(table_data: Table, filename: str, overwrite: bool = True, **kwargs) -> None:
    """Write the given table data to a file.

    Parameters
    ----------
    table_data : Table
        The table data to write.
    filename : str
        The name of the file to write the table data to.
    overwrite : bool, optional
        Whether to overwrite the file if it exists, by default True.

    Raises
    ------
    SystemExit
        If an error occurs during writing.
    """
    try:
        table_data.write(filename, overwrite=overwrite, **kwargs)
    except (ValueError, TypeError, OSError, IORegistryError) as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        # Replace \n with the system's line separator to ensure it's recognized by the logger
        message = template.format(type(ex).__name__, ex.args).replace("\\n", os.linesep)
        logger.error(message)
        sys.exit(1)


class MolecularProfile:
    """
    A class for analyzing meteorological data and generating atmospheric profiles.

    This class provides methods for retrieving meteorological data from various file formats,
    creating molecular number density profiles, computing mass density, and calculating
    the refractive index based on atmospheric conditions. It supports output in ``ecsv`` format.

    Methods
    -------
    get_data()
        Read and preprocess meteorological data from a specified file.
    create_atmospheric_profile(co2_concentration, outfile, reference_atmosphere, altitude_list)
        Generate a table with atmospheric parameters compatible with CORSIKA simulations and optionally write to a file.
    create_molecular_density_profile(mdp_file)
        Calculate molecular number density per altitude and optionally write to a file.
    create_rayleigh_extinction_profile(co2_concentration, wavelength_min, wavelength_max, rayleigh_extinction_file, reference_atmosphere, rayleigh_scattering_altitude_bins)
        Calculate the altitude profile of the optical depth due to Rayleigh scattering for a given range of wavelengths and optionally write to a file.
    create_molecular_absorption_profile(molecule_name, molecular_cross_section_file, wavelength_min, wavelength_max, molar_mass, molecular_absorption_file, altitude_bins)
        Calculate the altitude profile of the molecular absorption for a given range of wavelengths and optionally write to a file.
    create_refractive_index_profile(wavelength_min, wavelength_max, refractive_index_file)
        Calculate the refractive index profile for a given range of wavelengths and optionally write to a file.
    convert_to_simtel_compatible(input_ecsv_file, output_file, observation_altitude)
        Convert the extinction or absorption profile to a format compatible with simtelarray.
    """

    def __init__(
        self,
        data_file: str,
        stat_columns: list[str] = None,
    ):
        """
        Initialize an instance of the MolecularProfile class.

        Parameters
        ----------
        data_file : str
            The path to the txt file containing the data.
        stat_columns : list of str, optional
            A list of column names for statistical data. The default columns are
            Pressure, Altitude, Density, Temperature, Wind Speed, Wind Direction,
            Relative humidity, Exponential Density, and Ozone mass mixing ratio.

        Attributes
        ----------
        data_file : str
            The path to the data file provided during initialization.
        data : astropy.Table or None
            The main data table, initially set to None.
        stat_data : astropy.Table or None
            A table for statistical data, initially set to None.
        stat_description : dict of str: astropy.Table or None
            A dictionary mapping statistical descriptions to their respective tables,
            initially set to None.
        stat_columns : list of str
            The list of column names for statistical data.
        """
        self.data_file = data_file
        self.data = None
        self.stat_data = None
        self.stat_description = None
        if stat_columns:
            self.stat_columns = stat_columns
        else:
            self.stat_columns = [
                "Pressure",
                "Altitude",
                "Density",
                "Temperature",
                "Wind Speed",
                "Wind Direction",
                "Relative humidity",
                "Exponential Density",
                "Ozone mass mixing ratio",
            ]

    # ==================================================================================
    # Private functions
    # ==================================================================================

    def _compute_mass_density(
        self, air: str = "moist", co2_concentration: float = 415
    ) -> None:
        """
        Compute regular and exponential mass density of air.

        Adds to data the following columns:
        * 'Xw': molar fraction of water vapor (0 if air is dry)
        * 'Compressibility'
        * 'Mass Density'
        * 'Exponential Mass Density'

        Parameters
        ----------
        air : str
            Type of air, can be 'moist' or 'dry'
        co2_concentration : float
            CO2 volume concentration in ppmv
        """
        if air == "moist":
            self.data["Xw"] = molar_fraction_water_vapor(
                self.data["Pressure"],
                self.data["Temperature"],
                self.data["Relative humidity"],
            )
        elif air == "dry":
            self.data["Xw"] = 0.0
        else:
            raise ValueError("Wrong air condition. It must be 'moist' or 'dry'.")

        self.data["Compressibility"] = compressibility(
            self.data["Pressure"], self.data["Temperature"], self.data["Xw"]
        )
        self.data["Mass Density"] = density_moist_air(
            self.data["Pressure"],
            self.data["Temperature"],
            self.data["Compressibility"],
            self.data["Xw"],
            co2_concentration,
        )
        self.data["Exponential Mass Density"] = (
            self.data["Mass Density"] / STD_AIR_DENSITY
        ).decompose() * np.exp(
            (self.data["Altitude"] / DENSITY_SCALE_HEIGHT).decompose()
        )

    def _refractive_index(
        self, P: Quantity, T: Quantity, RH: float, wavelength: Quantity, CO2: float
    ) -> float:
        """
        Calculate the refractive index using the Rayleigh scattering model.

        Parameters
        ----------
        P : Quantity
            The atmospheric pressure at which to calculate the refractive index.
            Should have units of pressure (hPa).
        T : Quantity
            The temperature at which to calculate the refractive index.
            Should have units of temperature (K).
        RH : float
            The relative humidity as a percentage (0-100) at which to calculate
            the refractive index.
        wavelength : Quantity
            The wavelength of light for which to calculate the refractive index.
            Should have units of length (nm).
        CO2 : float
            The CO2 concentration in parts per million (ppm) at which to calculate
            the refractive index.

        Returns
        -------
        float
            The calculated refractive index for the given conditions.

        Notes
        -----
        This method utilizes the Rayleigh scattering model to compute the refractive
        index. It is dependent on atmospheric conditions such as pressure, temperature,
        relative humidity, and CO2 concentration.
        """
        rayleigh = Rayleigh(wavelength, CO2, P, T, RH)
        return rayleigh.refractive_index

    def _get_data_altitude_range(
        self, altitude_profile: Quantity
    ) -> tuple[Quantity, Quantity]:
        """
        Calculate the floor and ceiling of the available DAS data.

        Parameters
        ----------
        altitude_profile : Quantity
            Tuple with the altitudes that the atmospheric parameters will be calculated.
            Units of length.

        Returns
        -------
        m_floor, m_ceiling :
            Highest and lowest altitudes, where DAS data is available.
        """
        m_floor = take_closest(
            altitude_profile,
            (
                (self.stat_description["avg"]["Altitude"][-1])
                * (self.stat_description["avg"]["Altitude"].unit)
            ).to(altitude_profile.unit),
        )
        m_ceiling = take_closest(
            altitude_profile,
            (
                (self.stat_description["avg"]["Altitude"][0])
                * (self.stat_description["avg"]["Altitude"].unit)
            ).to(altitude_profile.unit),
        )
        return m_floor, m_ceiling

    def _create_profile(self, interpolation_centers: Quantity) -> dict[str, Quantity]:
        """
        Interpolate atmospheric parameters at specified altitudes.

        This method interpolates various atmospheric parameters (temperature, relative humidity, pressure, etc.)
        at the altitudes specified by `interpolation_centers`. The interpolation is based on the
        average atmospheric data stored in the class instance. The method returns a dictionary containing the interpolated
        values, making it easy to access specific atmospheric parameters by name.

        Parameters
        ----------
        interpolation_centers : Quantity
            The altitudes at which to interpolate the atmospheric parameters.
            Should have units of length (e.g., km).

        Returns
        -------
        parameters_dict : dict
            A dictionary where keys are the names of the atmospheric parameters (e.g., 'temperature', 'relative_humidity',
            etc.) and values are the interpolated quantities at the specified altitudes.
            Each Quantity in the dictionary has appropriate units.
        """
        parameters_dict = {}
        for col in self.stat_data.colnames:
            parameter = (
                interpolate(
                    self.stat_description["avg"]["Altitude"].to(u.km),
                    self.stat_description["avg"][col],
                    interpolation_centers.to(u.km),
                )
                * self.stat_description["avg"][col].unit
            )
            parameters_dict.update({col: parameter})
        return parameters_dict

    def _pick_up_reference_atmosphere(
        self,
        m_ceiling: Quantity,
        m_floor: Quantity,
        reference_atmosphere: Table | str,
    ) -> Table:
        """
        Select and return a portion of the reference atmosphere table based on specified altitude limits.

        This method merges the observational data with a reference atmosphere by selecting rows from the reference
        atmosphere table that are above a specified ceiling altitude or below a specified floor altitude. It is useful
        for extending observational data with standard atmospheric models to cover a wider altitude range.

        Parameters
        ----------
        m_ceiling : Quantity
            The ceiling altitude above which data from the reference atmosphere should be included.
            Should be an astropy Quantity with units of length (e.g., meters or kilometers).
        m_floor : Quantity
            The floor altitude below which data from the reference atmosphere should be included.
            Should be an astropy Quantity with units of length (e.g., meters or kilometers).
        reference_atmosphere : Table | str
            The reference atmosphere data, which can be provided as an Astropy Table or a file path to an ECSV file.

        Returns
        -------
        Table
            An Astropy Table containing the atmospheric profile data from the reference atmosphere that lies
            outside the specified altitude range (i.e., above the ceiling or below the floor).

        Raises
        ------
        Exception
            If reading the reference atmosphere file fails due to a TypeError, ValueError, or RuntimeError,
            the method logs the error and exits the program.

        Notes
        -----
        The method assumes that the reference atmosphere table contains an 'altitude' column against which
        the ceiling and floor altitudes are compared. The units of the 'altitude' column in the reference
        atmosphere table should be compatible with the units of `m_ceiling` and `m_floor`.
        """
        if isinstance(reference_atmosphere, Table):
            reference_atmosphere_table = reference_atmosphere
        else:
            try:
                reference_atmosphere_table = Table.read(reference_atmosphere)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                logger.error(message)
                sys.exit(1)
        mask = (
            reference_atmosphere_table["altitude"]
            >= m_ceiling.to(reference_atmosphere_table["altitude"].unit)
        ) | (
            reference_atmosphere_table["altitude"]
            <= m_floor.to(reference_atmosphere_table["altitude"].unit)
        )
        return reference_atmosphere_table[mask]

    def _wavelength_range(
        self,
        wavelength_min: Quantity = 200 * u.nm,
        wavelength_max: Quantity = 1001 * u.nm,
    ) -> Quantity:
        """
        Generate a range of wavelengths between specified minimum and maximum values.

        This method creates an array of wavelengths starting from `wavelength_min` up to `wavelength_max` with a step
        of 1 nm. It is used to prepare a consistent wavelength grid for various calculations, such as interpolating
        cross sections.

        Parameters
        ----------
        wavelength_min : Quantity, optional
            The minimum wavelength to include in the range, by default 200 nm.
        wavelength_max : Quantity, optional
            The maximum wavelength to include in the range, by default 1001 nm.

        Returns
        -------
        Quantity
            An array of wavelengths with a step of 1 nm, expressed as an astropy Quantity with units of nm.
        """
        return (
            np.arange(wavelength_min.to_value(u.nm), wavelength_max.to_value(u.nm), 1)
            * u.nm
        )

    def _interpolate_cross_section(self, molecular_cross_section_file: str) -> QTable:
        """
        Interpolates the molecular cross-section data to a standard wavelength range.

        This method reads the molecular cross-section data from a specified file, sorts it by wavelength,
        and then interpolates the cross-section values to match the standard wavelength range generated
        by `_wavelength_range`. The result is a table with two columns: wavelength and interpolated cross-section.

        Parameters
        ----------
        molecular_cross_section_file : str
            The file path to the molecular cross-section data stored in an ECSV (Enhanced Character Separated Values) format.

        Returns
        -------
        QTable
            An astropy QTable containing the wavelengths and their corresponding interpolated cross-section values.
            The table has two columns: "wavelength" and "cross section", both of which are astropy Quantities.
        """
        cross_section_table = QTable.read(
            molecular_cross_section_file, format="ascii.ecsv"
        )
        cross_section_table.sort("wavelength")
        wavelength_range = self._wavelength_range()
        cross_section_interpolated = (
            interpolate(
                cross_section_table["wavelength"],
                cross_section_table["x_section"],
                wavelength_range,
                kind="linear",
            )
            * u.cm**2
        )
        cross_section_interpolated_table = QTable(
            [wavelength_range, cross_section_interpolated],
            names=("wavelength", "cross section"),
        )
        return cross_section_interpolated_table

    # ==================================================================================
    # Main get data function
    # ==================================================================================
    def get_data(self) -> None:
        """
        Read and preprocesses meteorological data from a specified file.

        This method reads meteorological data from the file specified by `self.data_file`. It supports reading data
        in either ECMWF/GDAS grib (versions 1 and 2) or ECSV formats. For grib files, it extracts the data using a
        dedicated method and extends it with additional processing. For ECSV files, it directly reads the data into
        an Astropy Table. After reading the data, it computes a statistical description of selected columns grouped
        by pressure.

        Raises
        ------
        FileNotFoundError
            If the specified data file does not exist.
        NotImplementedError
            If the file format is neither grib (1 or 2) nor ECSV, indicating that the format is not supported.

        Notes
        -----
        The method updates the instance attributes `self.data` with the ingested data table, `self.stat_data` with
        the data table grouped by pressure, and `self.stat_description` with statistical descriptions (average, standard
        deviation, mean absolute deviation, peak-to-peak max, and peak-to-peak min) of the grouped data.
        """
        if not os.path.isfile(self.data_file):
            raise FileNotFoundError(f"The file '{self.data_file}' does not exist.")
        file_ext = os.path.splitext(self.data_file)[1]
        if file_ext in (".grib", ".grib2"):
            self.data = get_grib_file_data(self.data_file)
            self.data = extend_grib_data(self.data)
        elif file_ext == ".ecsv":
            self.data = Table.read(self.data_file)
        else:
            raise NotImplementedError(
                "Only grib (1,2) and ecsv formats are supported at the moment. "
                f"Requested format: {file_ext}"
            )
        self.stat_data = self.data[self.stat_columns].group_by("Pressure")
        self.stat_description = {
            "avg": self.stat_data.groups.aggregate(np.mean),
            "std": self.stat_data.groups.aggregate(np.std),
            "mad": self.stat_data.groups.aggregate(
                lambda x: np.mean(np.absolute(x - np.mean(x)))
            ),
            "p2p_max": self.stat_data.groups.aggregate(
                lambda x: np.max(x) - np.mean(x)
            ),
            "p2p_min": self.stat_data.groups.aggregate(
                lambda x: np.mean(x) - np.min(x)
            ),
        }

    def create_atmospheric_profile(
        self,
        co2_concentration: float,
        outfile: str | None = None,
        reference_atmosphere: Table | str | None = None,
        altitude_list: Quantity = STD_CORSIKA_ALTITUDE_PROFILE,
    ) -> Table:
        """
        Generate a table with atmospheric parameters for CORSIKA simulations.

        This method computes atmospheric parameters at specified altitudes and optionally writes them to an ECSV file.
        The table includes altitude, density, thickness, refractive index minus one, temperature, pressure, and partial
        water vapor pressure at each altitude step.

        The table includes the following columns:

        - ``altitude``: Altitude in kilometers. Computed atmospheric parameters are provided at these altitudes.
        - ``atmospheric_density``: Atmospheric density in grams per cubic centimeter.
        - ``atmospheric_thickness``: Atmospheric thickness in grams per square centimeter.
          This is calculated from pressure divided by the standard gravitational acceleration.
        - ``refractive_index_m_1``: Relative refractive index minus one.
          This is calculated based on pressure, temperature, relative humidity, a wavelength of 350 nm, and CO2 concentration.
        - ``temperature``: Temperature in Kelvins at the specified altitude.
        - ``pressure``: Pressure in hPa at the specified altitude.
        - ``partial_water_pressure``: Partial water vapor pressure in the same units as pressure, normalized by total pressure.

        Parameters
        ----------
        co2_concentration : float
            The CO2 concentration value to use in the atmospheric model converted to ppm.
        outfile : Optional[str], default=None
            The path and name of the output file. If None, the method will not write to a file but will still return the table.
        reference_atmosphere : Table | str | None, default=None
            The reference atmosphere data, which can be provided as an Astropy Table or a file path to an ECSV file,
            This is used to extend or fill in data beyond the range covered by the input data.
            If not provided, the method will be constrained to the extent of the provided meteorological data.
        altitude_list : Quantity, default=STD_CORSIKA_ALTITUDE_PROFILE
            An array of altitudes at which to calculate atmospheric parameters. Should be an astropy Quantity
            with units of length.

        Returns
        -------
        Table
            An Astropy Table containing the computed atmospheric parameters at specified altitudes, formatted for
            CORSIKA simulations.

        Notes
        -----
        The method calculates atmospheric parameters based on the provided meteorological data and reference atmosphere.
        It interpolates or extrapolates as necessary to cover the specified altitude range. The output table is suitable
        for use in preparing CORSIKA atmospheric profiles, though it requires conversion to CORSIKA's format.
        """
        m_floor, m_ceiling = self._get_data_altitude_range(
            altitude_list.to(self.stat_description["avg"]["Altitude"].unit)
        )
        altitude = altitude_list[
            (altitude_list.to_value() > m_floor.to_value(altitude_list.unit))
            & (altitude_list.to_value() < m_ceiling.to_value(altitude_list.unit))
        ]
        altitude = altitude.to(self.stat_description["avg"]["Altitude"].unit)
        profiles = self._create_profile(altitude)
        temperature = profiles["Temperature"]
        relative_humidity = profiles["Relative humidity"]
        pressure = profiles["Pressure"]
        density = profiles["Density"] / N0_AIR
        thickness = pressure / STD_GRAVITATIONAL_ACCELERATION
        rel_water_vapor_pressure = (
            partial_pressure_water_vapor(temperature, relative_humidity) / pressure
        ).decompose()
        rel_refractive_index = (
            self._refractive_index(
                pressure,
                temperature,
                relative_humidity,
                350.0 * u.nm,
                co2_concentration,
            )
            - 1.0
        )

        tables = []

        for i in np.arange(len(altitude)):
            outdict = {
                "altitude": altitude[i].to(u.km),
                "atmospheric_density": density[i].to(u.g / u.cm**3),
                "atmospheric_thickness": thickness[i].decompose().to(u.g / u.cm**2),
                "refractive_index_m_1": rel_refractive_index[i],
                "temperature": temperature[i],
                "pressure": pressure[i],
                "partial_water_pressure": rel_water_vapor_pressure[i],
            }
            tables.append(outdict)
        # Merge ECMWF profile with upper atmospheric profile
        if reference_atmosphere:
            reference_atmosphere_table = self._pick_up_reference_atmosphere(
                m_ceiling, m_floor, reference_atmosphere
            )
            tables.append(reference_atmosphere_table)
        else:
            logger.warning(
                "Since reference atmosphere was not provided, "
                "the resulting atmospheric model will be constrained "
                "to the extent of the provided meteorological data."
            )
        corsika_input_table = vstack(tables)
        corsika_input_table.sort("altitude")
        if outfile:
            _write(corsika_input_table, outfile)
        return corsika_input_table

    def create_molecular_density_profile(self, mdp_file: str | None = None) -> Table:
        """
        Calculate the altitude profile of the molecular number density.

        This method calculates the molecular number density at specified altitudes ranging from 0 to 20,000 meters,
        with a step of 1,000 meters. The number density is interpolated from the statistical description of the
        atmospheric data previously loaded. The results can be optionally written to an ECSV file.

        Parameters
        ----------
        mdp_file : str | None, default=None
            The path and name of the output file where the molecular number density profile will be saved.
            If None, the data is not written to a file.

        Returns
        -------
        Table
            An Astropy Table containing the calculated molecular number densities at specified altitudes.

        Notes
        -----
        The molecular number density is calculated based on the average density values from the atmospheric data.
        The altitudes are converted to the same unit as the altitude in the statistical description before interpolation.
        This method is useful for atmospheric studies and simulations that require detailed altitude profiles.
        """
        altitudes = np.arange(0.0, 20000.0, 1000) * u.m
        altitudes = altitudes.to(self.stat_description["avg"]["Altitude"].unit)
        number_density = (
            interpolate(
                self.stat_description["avg"]["Altitude"],
                self.stat_description["avg"]["Density"],
                altitudes,
            )
            * self.stat_description["avg"]["Density"].unit
        )
        t = Table([altitudes, number_density], names=["altitude", "number density"])
        if mdp_file:
            _write(t, mdp_file)
        return t

    def create_rayleigh_extinction_profile(
        self,
        co2_concentration: float,
        wavelength_min: Quantity = 200 * u.nm,
        wavelength_max: Quantity = 700 * u.nm,
        rayleigh_extinction_file: str | None = None,
        reference_atmosphere: Table | str | None = None,
        rayleigh_scattering_altitude_bins: Quantity = RAYLEIGH_SCATTERING_ALTITUDE_BINS,
    ) -> Table:
        """
        Calculate the altitude profile of the optical depth due to Rayleigh scattering for a given range of wavelengths.

        The optical depth (AOD) for an altitude h over the observatory is given by
        the integral of the monochromatic volume coefficient beta,
        with integration limits h_obs up to h.
        It is provided per altitude bins as a function of wavelength.

        Parameters
        ----------
        co2_concentration : float
            The CO2 concentration (in ppm) to use for calculating the Rayleigh scattering coefficient.
        wavelength_min : Quantity, default=200 * u.nm
            The minimum wavelength for which the Rayleigh extinction profile should be calculated.
        wavelength_max : Quantity, default=700 * u.nm
            The maximum wavelength for which the Rayleigh extinction profile should be calculated.
        rayleigh_extinction_file : str | None, default=None
            The path and name of the output file where the Rayleigh extinction profile will be saved.
            If None, the data is not written to a file.
        reference_atmosphere : Table | str | None, default=None
            The reference atmosphere data, which can be provided as an Astropy Table or a file path to an ECSV file,
            This is used to extend or fill in data beyond the range covered by the input data.
            If not provided, the method will be constrained to the extent of the provided meteorological data.

        rayleigh_scattering_altitude_bins : Quantity, default=RAYLEIGH_SCATTERING_ALTITUDE_BINS
            Tuple with the altitudes that the AOD will be calculated. Units of length.
        write_to_file : bool
            If true, the function writes the Rayleigh scattering extinction
            table into the file `rayleigh_extinction_file`

        Returns
        -------
        Table
            A table containing the calculated Rayleigh extinction profile for each altitude bin and wavelength.
            The results are written to the specified file if `rayleigh_extinction_file` is provided.
        """
        m_floor, m_ceiling = self._get_data_altitude_range(
            rayleigh_scattering_altitude_bins
        )
        altitude = rayleigh_scattering_altitude_bins.to(u.km)
        altitude = altitude[altitude < m_ceiling]

        interpolation_centers = (altitude[:-1] + altitude[1:]) / 2
        profiles = self._create_profile(interpolation_centers)
        temperature_lower = profiles["Temperature"]
        relative_humidity_lower = profiles["Relative humidity"]
        pressure_lower = profiles["Pressure"]

        # Concatenate with reference atmosphere
        if reference_atmosphere:
            reference_atmosphere_table = self._pick_up_reference_atmosphere(
                m_ceiling, m_floor, reference_atmosphere
            )
            length_of_columns = len(reference_atmosphere_table)
            relative_humidity_upper = (
                np.zeros(length_of_columns)
                * self.stat_description["avg"]["Relative humidity"].unit
            )
            relative_humidity = np.concatenate(
                (relative_humidity_lower, relative_humidity_upper)
            )
            pressure = np.concatenate(
                (pressure_lower, reference_atmosphere_table["pressure"])
            )
            temperature = np.concatenate(
                (temperature_lower, reference_atmosphere_table["temperature"])
            )
            altitude = np.concatenate(
                (altitude, reference_atmosphere_table["altitude"])
            )
        else:
            logger.warning(
                "Since the reference atmosphere was not provided, "
                "the resulting atmospheric model will be constrained "
                "to the extent of the provided meteorological data."
            )
            temperature = temperature_lower
            pressure = pressure_lower
            relative_humidity = relative_humidity_lower

        t = QTable(
            [altitude[1:], pressure, temperature, relative_humidity],
            names=("altitude", "pressure", "temperature", "relative_humidity"),
        )
        t.sort("altitude")
        bin_widths = np.diff(np.sort(altitude))
        t["bin_widths"] = bin_widths
        mask = t["altitude"] > m_floor
        wavelength_range = (
            np.arange(wavelength_min.to_value(u.nm), wavelength_max.to_value(u.nm), 1)
            * u.nm
        )
        aod_units = len(wavelength_range) * [1 * u.dimensionless_unscaled]
        rayleigh_extinction_table = Table(names=wavelength_range, units=aod_units)
        col_alt_max = Column(name="altitude_max", unit=u.km)
        col_alt_min = Column(name="altitude_min", unit=u.km)
        rayleigh_extinction_table.add_columns(
            [col_alt_max, col_alt_min], indexes=[0, 0]
        )
        aod_dict = {
            aod: 0
            for aod in np.arange(
                wavelength_min.to_value(u.nm), wavelength_max.to_value(u.nm)
            )
        }
        for row in t[mask]:
            new_row = []
            new_row.append(row["altitude"])
            new_row.append(row["altitude"] - row["bin_widths"])
            for wavelength in wavelength_range:
                rayleigh = Rayleigh(
                    wavelength,
                    co2_concentration,
                    row["pressure"],
                    row["temperature"],
                    row["relative_humidity"],
                )
                beta = rayleigh.beta
                aod = row["bin_widths"] * beta
                aod_dict[wavelength.to_value(u.nm)] += aod
                new_row.append(aod_dict[wavelength.to_value(u.nm)])
            rayleigh_extinction_table.add_row(new_row)
        if rayleigh_extinction_file:
            _write(rayleigh_extinction_table, rayleigh_extinction_file)
        return rayleigh_extinction_table

    def create_molecular_absorption_profile(
        self,
        molecule_name: str,
        molecular_cross_section_file: str,
        wavelength_min: Quantity = 200 * u.nm,
        wavelength_max: Quantity = 700 * u.nm,
        molar_mass: Quantity = MOLAR_MASS_OZONE,
        molecular_absorption_file: str | None = None,
        altitude_bins: Quantity = RAYLEIGH_SCATTERING_ALTITUDE_BINS,
    ) -> QTable:
        """
        Calculate the optical depth due to molecular absorption for a given range of wavelengths and altitudes.

        This method computes the molecular absorption optical depth by multiplying the absorption cross section
        (a function of wavelength) with the molecular number density (a function of altitude). The results are
        compiled into a table, which includes the ozone number density for each altitude bin and wavelength
        in the specified range.

        Parameters
        ----------
        molecule_name : str
            The name of the molecule for which the absorption profile should be calculated.
        molecular_cross_section_file : str
            The path to the file containing the molecular absorption cross section data.
        wavelength_min : Quantity, default=200 * u.nm
            The minimum wavelength for which the molecular absorption profile should be calculated.
        wavelength_max : Quantity, default=700 * u.nm
            The maximum wavelength for which the molecular absorption profile should be calculated.
        molar_mass : Quantity, default=MOLAR_MASS_OZONE
            The molar mass of the molecule for which the absorption profile should be calculated.
        molecular_absorption_file : str, optional
            The path and name of the output file where the molecular absorption profile will be saved.
        altitude_bins : Quantity, default=RAYLEIGH_SCATTERING_ALTITUDE_BINS
            The altitude bins (in units of length) for which the molecular absorption optical depth will be calculated.

        Returns
        -------
        QTable
            An Astropy QTable containing the molecular absorption optical depth per altitude bin and per wavelength bin.
            The table includes columns for altitude, density, mixing ratio, and number density.

        Notes
        -----
        The molecular number density is calculated from the molecule mixing ratio and the mass density of the atmosphere,
        using the ideal gas law. The absorption cross section data must be provided in a file, which this method
        will read and interpolate as necessary to match the specified wavelength range.
        """
        cross_section_table = self._interpolate_cross_section(
            molecular_cross_section_file
        )
        altitude = altitude_bins.to(u.km)
        interpolation_centers = (altitude[:-1] + altitude[1:]) / 2
        profiles = self._create_profile(interpolation_centers)
        mass_density = profiles["Density"] / N0_AIR
        mass_density[np.isnan(mass_density)] = 0
        molecule_mixing_ratio = profiles[f"{molecule_name} mass mixing ratio"]
        molecule_mixing_ratio[np.isnan(molecule_mixing_ratio)] = 0
        molecule_profile_table = QTable(
            [altitude[1:], mass_density.to(u.g / u.cm**3), molecule_mixing_ratio],
            names=("altitude", "density", "mixing_ratio"),
        )
        molecule_profile_table["number_density"] = (
            molecule_profile_table["mixing_ratio"]
            * molecule_profile_table["density"]
            * (N_A / molar_mass)
        ).decompose()
        molecule_profile_table.sort("altitude")
        molecule_profile_table["bin_widths"] = np.diff(np.sort(altitude))

        wavelength_range = self._wavelength_range(wavelength_min, wavelength_max)
        molecular_absorption_table = Table(names=wavelength_range)
        col_alt_max = Column(name="altitude_max", unit=u.km)
        col_alt_min = Column(name="altitude_min", unit=u.km)
        molecular_absorption_table.add_columns(
            [col_alt_max, col_alt_min], indexes=[0, 0]
        )
        aod_dict = {aod: 0 for aod in wavelength_range.to_value(u.nm)}
        for row in molecule_profile_table:
            new_row = []
            new_row.append(row["altitude"])
            new_row.append(row["altitude"] - row["bin_widths"])
            for wavelength in wavelength_range:
                mask = cross_section_table["wavelength"] == wavelength
                cross_section_table_masked = cross_section_table[mask]
                beta = (
                    row["number_density"] * cross_section_table_masked["cross section"]
                )
                beta = beta.decompose()
                if np.isnan(beta):
                    beta = 0
                aod = row["bin_widths"].to(u.m) * beta
                aod_dict[wavelength.to_value(u.nm)] += aod
                new_row.append(aod_dict[wavelength.to_value(u.nm)])
            molecular_absorption_table.add_row(new_row)

        if molecular_absorption_file:
            _write(molecular_absorption_table, molecular_absorption_file)
        return molecular_absorption_table

    # ==================================================================================
    # helper functions
    # ==================================================================================

    def timeseries_analysis(
        self,
        outfile: str,
        parameter_level: Quantity,
        atmospheric_parameter: str,
        interpolation_parameter: str,
        m_floor: Quantity,
        m_ceiling: Quantity,
        interpolation_list: Quantity,
    ) -> None:
        """
        Analyze timeseries of meteorological data at a specified altitude level.

        This method processes meteorological data to produce a timeseries analysis for a given atmospheric
        parameter (e.g., number density, temperature, pressure, relative humidity) at a specified altitude/pressure
        level. The analysis is focused between specified lower and upper altitude or pressure level bounds
        (m_floor and m_ceiling). The result is an Astropy table containing the provided atmospheric parameter
        at the specified level as a function of the Modified Julian Date (MJD). This table is then saved to a
        specified output file. The timeseries analysis can be used for various purposes, such as identifying
        seasons or validating data assimilation systems (DAS) against local weather station observations.

        Parameters
        ----------
        outfile : str
            The path and name of the output file where the resulting table will be stored.
        parameter_level : Quantity
            The specific altitude/pressure level at which the timeseries analysis will be conducted. This is
            typically chosen based on where significant seasonal differences are observed or where validation
            against local observations is desired.
        atmospheric_parameter : str
            The atmospheric parameter to analyze in the timeseries. Common choices include number density
            (for season definition) and temperature, pressure, or relative humidity (for DAS validation).
        interpolation_parameter : str
        m_floor : Quantity
            The lowest level to consider in the analysis. This defines the lower bound of the parameter range.
        m_ceiling : Quantity
            The highest level to consider in the analysis. This defines the upper bound of the parameter range.
        interpolation_list : Quantity, optional
            A sequence of altitudes or pressure levels at which the atmospheric parameters will be calculated.
            This list should cover the range between m_floor and m_ceiling.

        Notes
        -----
        The method assumes that the input data includes a 'Timestamp' column that can be converted to MJD
        for the timeseries analysis. The atmospheric parameter values are interpolated for the specified
        altitude/pressure level across the provided interpolation list within the bounds of m_floor and m_ceiling.
        """
        tables = []
        interpolation_centers = interpolation_list[
            (interpolation_list.to_value() >= m_floor.to_value(interpolation_list.unit))
            & (
                interpolation_list.to_value()
                < m_ceiling.to_value(interpolation_list.unit)
            )
        ]
        self.data["MJD"] = self.data["Timestamp"].mjd
        test_table = self.data.group_by("MJD")
        indices = test_table.groups.indices
        for first, second in zip(indices, indices[1:]):
            t = test_table[first:second].group_by("Pressure").groups.aggregate(np.mean)
            parameter = (
                interpolate(
                    t[interpolation_parameter],
                    t[atmospheric_parameter],
                    interpolation_centers,
                )
                * t[atmospheric_parameter].unit
            )
            current_table = QTable(
                [parameter, interpolation_centers],
                names=(atmospheric_parameter, interpolation_parameter),
            )
            current_table["mjd"] = t["MJD"][1]
            mask = current_table[interpolation_parameter] == parameter_level
            tables.append(current_table[mask])
        output_table = vstack(tables)
        _write(output_table, outfile)
        del tables

    def stat_analysis(self, atmo_parameter, altitudes, outfile):
        """
        Perform statistical analysis on an atmospheric parameter and save the results.

        This function interpolates the average, standard deviation, interquantile range, peak-to-peak maximum,
        and peak-to-peak minimum values of a given atmospheric parameter at specified altitudes.
        The results are stored in an output file as a table.

        Parameters
        ----------
        atmo_parameter : str
            The name of the atmospheric parameter to analyze (e.g., "Temperature", "Pressure").
        altitudes : astropy.units.Quantity
            An array of altitude values with units of length (e.g., km, m).
        outfile : str
            The output file path where the atmospheric parameter profile will be saved.
        """
        altitudes_km = altitudes.to(u.km)
        ref_altitudes = self.stat_description["avg"]["Altitude"].to(u.km)

        stat_categories = ["avg", "std", "p2p_max", "p2p_min"]
        atmo_param_values = {
            stat: interpolate(
                ref_altitudes, self.stat_description[stat][atmo_parameter], altitudes_km
            )
            * self.stat_description["avg"][atmo_parameter].unit
            for stat in stat_categories
        }
        atmo_param_profile = Table(
            [altitudes, *atmo_param_values.values()],
            names=(
                "altitude",
                "atmo_param",
                "atmo_param_std",
                "atmo_param_p2p_max",
                "atmo_param_p2p_min",
            ),
        )

        atmo_param_profile.write(outfile, overwrite=True)
