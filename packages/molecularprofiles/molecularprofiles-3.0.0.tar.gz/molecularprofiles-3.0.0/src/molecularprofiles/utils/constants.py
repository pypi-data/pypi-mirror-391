"""Constants definitions."""

import astropy.units as u
from astropy.constants import N_A

# standard atmosphere thermodynamic values
STD_NUMBER_DENSITY = (
    2.546899e19 / u.cm**3
)  # [cm^-3] molecular number density for standard air conditions
STD_AIR_PRESSURE = 1013.25 * u.hPa  # [hPa]   standard air pressure
STD_AIR_TEMPERATURE = 288.15 * u.K  # [K]     standard air temperature
STD_AIR_DENSITY = 1.225 * u.kg / u.m**3  # [kg/m^3] standard air density
DENSITY_SCALE_HEIGHT = 9500.0 * u.m  # [km]    density scale height for La Palma Winter
STD_RELATIVE_HUMIDITY = 45.9 * u.percent  # [%]     standard air rel. humidity
# atmospheric composition
NITROGEN_RATIO = 0.78084 * u.dimensionless_unscaled
OXYGEN_RATIO = 0.20946 * u.dimensionless_unscaled
ARGON_RATIO = 0.00934 * u.dimensionless_unscaled
GAS_CONSTANT = 8.31451 * u.J / (u.K * u.mol)  # gas constant [J/mol/K]
MOLAR_MASS_WATER_VAPOR = 0.018015 * u.kg / u.mol  # molar mass of water vapor [kg/mol]
MOLAR_MASS_AIR = 0.0289644 * u.kg / u.mol  # molar mass of air [kg/mol]
MOLAR_MASS_OZONE = 0.048 * u.kg / u.mol  # molar mass of ozone [kg/mol]
MOLAR_MASS_NITROGEN_DIOXIDE = (
    0.0460055 * u.kg / u.mol
)  # molar mass of nitrogen dioxide [kg/mol]
# misc physics constants
STD_GRAVITATIONAL_ACCELERATION = (
    9.80665 * u.m / u.s**2
)  # standard acceleration of free fall [m/s^2]
STD_EARTH_RADIUS = 6245 * u.km  # Earth radius for geopotential height conversion [km]
N0_AIR = N_A / MOLAR_MASS_AIR
STD_CORSIKA_ALTITUDE_PROFILE = (
    0.0,
    1000.0,
    2000.0,
    3000.0,
    4000.0,
    5000.0,
    6000.0,
    7000.0,
    8000.0,
    9000.0,
    10000.0,
    11000.0,
    12000.0,
    13000.0,
    14000.0,
    15000.0,
    16000.0,
    17000.0,
    18000.0,
    19000.0,
    20000.0,
    21000.0,
    22000.0,
    23000.0,
    24000.0,
    25000.0,
    26000.0,
    27000.0,
    28000.0,
    29000.0,
    30000.0,
    32000.0,
    34000.0,
    36000.0,
    38000.0,
    40000.0,
    42000.0,
    44000.0,
    46000.0,
    48000.0,
    50000.0,
    55000.0,
    60000.0,
    65000.0,
    70000.0,
    75000.0,
    80000.0,
    85000.0,
    90000.0,
    95000.0,
    100000.0,
    105000.0,
    110000.0,
    115000.0,
    120000.0,
) * u.m
RAYLEIGH_SCATTERING_ALTITUDE_BINS = (
    2.1,
    2.2,
    2.3,
    2.4,
    2.6,
    2.8,
    3.1,
    3.5,
    4.0,
    4.5,
    5.0,
    5.5,
    6.0,
) * u.km
