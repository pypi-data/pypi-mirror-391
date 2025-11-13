from abc import abstractmethod
from enum import Enum

import geopandas as gpd

from libadalina_core.exceptions.input_file_exception import InputFileException

class RoadTypes(Enum):
    """Enum representing different types of roads for filtering purposes."""

    ALL = 'all'
    """Keep all roads."""
    CAR_ONLY = 'only_car'
    """Keep only roads accessible by car."""
    MAIN_ROADS = 'main_roads'
    """Keep only main roads (motorways, trunks, primary)."""

class MandatoryColumns(Enum):
    """Enum representing mandatory columns required in the input DataFrame."""

    id = 'id'
    road_name = 'name'
    oneway = 'oneway'

class OneWay(Enum):
    """Enum representing road directions."""

    Forward = 'forward'
    """Follows the direction of the geometry."""
    Backward = 'backward'
    """Goes against the direction of the geometry."""
    Both = 'both'
    """Both directions are allowed."""

class MapReader:

    def __init__(self, road_types: RoadTypes = RoadTypes.ALL):
        """
        Initialize the MapReader with the specified road type filter.

        Parameters
        ----------
        road_types : RoadTypes, optional
            The type of roads to keep. Default is RoadTypes.ALL, which keeps all roads.
        """
        self._road_types = road_types

    @abstractmethod
    def _filter_roads(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Filter roads based on the specified road type.
        This method should be implemented by subclasses to apply specific filtering logic.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def map_and_reduce(self, gdf: gpd.GeoDataFrame, column_map: dict[MandatoryColumns, str]) -> gpd.GeoDataFrame:
        """
        Remap column names and project only mandatory columns.

        Parameters
        ----------
        gdf : geopandas.GeoDataFrame
            The input GeoDataFrame to be processed.
        column_map : dict[MandatoryColumns, str]
            The column names mapping: keys are the expected column names (as defined in the MandatoryColumns enum),
            values are the actual column names in the input GeoDataFrame.

        Returns
        -------
        geopandas.GeoDataFrame
            A GeoDataFrame containing only the mandatory columns with standardized names.
        """
        for key, value in column_map.items():
            gdf[key.value] = gdf[value]

        gdf = gdf[['geometry'] + [c.value for c in MandatoryColumns]]

        for c in MandatoryColumns:
            if c.value not in gdf.columns:
                raise InputFileException(f"missing column {c.value} in dataframe")
        return gdf


