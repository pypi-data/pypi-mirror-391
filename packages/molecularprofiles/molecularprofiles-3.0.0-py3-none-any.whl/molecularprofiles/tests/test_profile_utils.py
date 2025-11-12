import os
from importlib.resources import files

import astropy.units as u
from molecularprofiles.tests import test_data
from molecularprofiles.utils.profiles_utils import (
    convert_to_simtel_compatible,
)


def test_convert_to_simtel_compatible():
    # Define test parameters
    input_ecsv_file = files(test_data).joinpath(
        "ecsv/test_rayleigh_extinction_file.ecsv"
    )
    output_file = "test_rayleigh_extinction_profile_simtel.dat"
    observation_altitude = u.Quantity(5000, unit="m")
    # Test convert_to_simtel_compatible method
    convert_to_simtel_compatible(input_ecsv_file, output_file, observation_altitude)
    # Perform assertions
    assert os.path.isfile(output_file)
    os.remove(output_file)
