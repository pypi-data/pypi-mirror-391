import pytest

from libadalina_core.sedona_utils import EPSGFormats
from libadalina_core.sedona_utils.coordinate_formats import epsg_from_code


@pytest.mark.parametrize("epsg_code,epsg_value", [
    (4326, EPSGFormats.EPSG4326),
    (32633, EPSGFormats.EPSG32633)
    ])
def test_epsg_parsing(epsg_code, epsg_value):
    assert epsg_from_code(epsg_code) == epsg_value
