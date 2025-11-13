import pytest
import pathlib

from libadalina_core.readers import geopackage_to_dataframe
from libadalina_core.spatial_operators import perimeter
SAMPLE_DIR = pathlib.Path(__file__).parent / "samples"


@pytest.mark.parametrize("area_id,expected_perimeter", [
    (215, 29057),
    (365, 49456)
    ])
def test_perimeter_of_geometries(area_id, expected_perimeter):
    path = SAMPLE_DIR / 'flows' / 'Shape_Matrice_OD2016_-_Veicoli_commerciali_e_pesanti_-_Zone_interne_20250816.gpkg'
    df = geopackage_to_dataframe(str(path))
    df = df[df['ID_Z_IIL'] == area_id]
    df = perimeter(df)

    assert round(df.first()['perimeter']) == expected_perimeter
