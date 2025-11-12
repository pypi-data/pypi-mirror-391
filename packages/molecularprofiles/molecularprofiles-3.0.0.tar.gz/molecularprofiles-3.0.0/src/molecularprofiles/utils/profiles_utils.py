"""Set of utilities for combining and converting extinction profiles."""

import astropy.units as u
from astropy.table import QTable, Table
from astropy.units import Quantity


def convert_to_simtel_compatible(
    input_ecsv_file: str, output_file: str, observation_altitude: Quantity
) -> None:
    """
    Convert an extinction profile from ECSV format to a format compatible with sim_telarray.

    Parameters
    ----------
    input_ecsv_file : str
        The path to the input file containing the extinction profile in ECSV format.
    output_file : str
        The path to the output file where the sim_telarray-compatible extinction profile
        will be saved.
    observation_altitude : Quantity
        The observation altitude, measured from sea level, to be included in the header
        of the output file. This should be provided as an astropy Quantity with units.

    Notes
    -----
    The output file will include a header line starting with '# H2= ' followed by the
    observation altitude (H2) in kilometers, and 'H1= ' followed by the maximum altitude
    for each bin (H1) in kilometers. Each subsequent line represents the extinction data
    for a specific wavelength, with the wavelength in the first column and the extinction
    values for each altitude bin in the following columns.
    """
    extinction_table = QTable.read(input_ecsv_file)
    with open(output_file, "w", encoding="utf-8") as f:
        H2 = observation_altitude.to_value(u.km)
        H1 = extinction_table["altitude_max"].to_value(u.km)
        list_of_altitude_bins = f"# H2= {H2:.3f}, H1= "
        for height in H1:
            list_of_altitude_bins += f"{height:.3f}\t"
        list_of_altitude_bins += "\n"
        f.writelines(list_of_altitude_bins)
        for wl in extinction_table.columns:
            if wl not in ("altitude_max", "altitude_min"):
                file_line = [str(wl).split(" ", maxsplit=1)[0], "\t"]
                for aod in extinction_table[wl]:
                    file_line += [f"{aod:.6f}", "\t"]
                file_line += ["\n"]
                f.writelines(file_line)


def combine_extinction_profiles(
    extinction_table_1: Table,
    extinction_table_2: Table,
    combined_file: str | None = None,
) -> Table:
    """
    Create an extinction profile by combining two profiles according to Beer-Lambert law.

    This function was originally created in order to combine Rayleigh scattering and molecular
    absorption data provided in an Astropy Tables in order to produce a MEP. The combined extinction data
    is then saved to a new file if a file name is provided, or returned as an Astropy Table.

    Parameters
    ----------
    extinction_table_1 : Table
        An Astropy Table containing an extinction profile corresponding to an atmospheric extinction process.
        This table should contain absolute optical depth per altitude bin per wavelength bin.
    extinction_table_2 : Table
        An Astropy Table containing a second extinction profile. This table should include the optical
        depth per altitude bin per wavelength bin due to molecular absorption.
    combined_file : Optional[str], default=None
        The path where the combined extinction profile should be saved. If None, the profile
        is not saved to a file but returned as an Astropy Table.

    Returns
    -------
    Table
        An Astropy Table containing the combined molecular extinction profile, featuring the absolute
        optical depth per altitude bin per wavelength bin. This table includes contributions from both
        Rayleigh scattering and molecular absorption.

    Notes
    -----
    The function assumes that the altitude bins and wavelength bins in the Rayleigh scattering data and
    the molecular absorption data match. If the bins do not match, the results may not accurately represent
    the combined extinction profile.
    """
    molecular_extinction_table = extinction_table_1.copy()
    for col_ma, col_rs in zip(
        extinction_table_2.columns, molecular_extinction_table.columns
    ):
        if col_ma != "altitude_max" and col_ma != "altitude_min":
            molecular_extinction_table[col_rs] = (
                extinction_table_2[col_ma] + molecular_extinction_table[col_rs]
            )
    if combined_file:
        molecular_extinction_table.write(combined_file, overwrite=True)
    return molecular_extinction_table
