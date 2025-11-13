from pyproj.database import query_crs_info
from enum import Enum

epsg_crs_list = query_crs_info(auth_name='EPSG')
enum_dict = {
    f"EPSG{crs.code}": int(crs.code)
    for crs in epsg_crs_list
    if crs.code.isdigit()
}

EPSGFormats = Enum('EPSGFormats', enum_dict)

def epsg_from_code(code: int) -> EPSGFormats:
    """
    Get the EPSG format from its integer code.

    Parameters
    ----------
    code : int
        Integer code representing the EPSG format.

    Returns
    -------
    EPSGFormats
        The corresponding EPSGFormats.

    Raises
    ------
    ValueError
        If no EPSG format is found for the given code.

    """
    for f in EPSGFormats:
        if f.value == code:
            return f
    raise ValueError(f"No EPSG format found for code {code}")

"""
Default EPSG format used in libadalina.

All DataFrame are converted upon reading and writing to this format.
"""
DEFAULT_EPSG = EPSGFormats.EPSG4326