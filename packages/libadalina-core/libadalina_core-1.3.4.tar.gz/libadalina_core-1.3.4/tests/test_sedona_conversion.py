import pytest
import pathlib

from libadalina_core.readers import geopackage_to_dataframe
from libadalina_core.sedona_utils import to_spark_dataframe

SAMPLE_DIR = pathlib.Path(__file__).parent / "samples"

@pytest.mark.parametrize("path", [
        f"{SAMPLE_DIR}/healthcare/EU_healthcare.gpkg",
        f"{SAMPLE_DIR}/regions/NUTS_RG_20M_2024_4326.gpkg",
    ])
def test_sedona_conversion_of_geopackage(path):
    df = geopackage_to_dataframe(str(path))
    df = to_spark_dataframe(df)
    assert df is not None
