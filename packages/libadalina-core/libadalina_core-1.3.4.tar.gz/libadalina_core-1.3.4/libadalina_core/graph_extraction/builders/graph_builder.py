import networkx as nx
import shapely
from pyspark.sql import Column
import pyspark.sql as ps
from sedona.sql import ST_Points, ST_Dump, ST_LineSegments, ST_Intersects, ST_Length, ST_LengthSpheroid

from libadalina_core.sedona_utils import DataFrame
from libadalina_core.spatial_operators import spatial_join, spatial_aggregation, AggregationFunction, JoinType, polygonize

from libadalina_core.graph_extraction.readers import MandatoryColumns, OneWay
from pyspark.sql import functions as F

from libadalina_core.sedona_utils import to_spark_dataframe

def all_columns_except_geometry(df: ps.DataFrame):
    return [F.col(c) for c in df.columns if c != 'geometry']

def get_column_name(col: Column) -> str:
    return col._jc.toString().split('.')[-1]

def explode_multipoint_to_points(df: ps.DataFrame) -> ps.DataFrame:
    return (df
            .select(F.explode(ST_Dump(ST_Points(F.col("geometry")))).alias("geometry"))
            .distinct()).select(F.monotonically_increasing_id().alias('uuid'), F.col('geometry'))

def explode_multiline_to_lines(df: ps.DataFrame) -> ps.DataFrame:
    return (df
            .select(*all_columns_except_geometry(df),
                    F.explode(ST_LineSegments(F.col("geometry"))).alias('geometry'))
            ).withColumn('distance', ST_LengthSpheroid(F.col('geometry')))

def join_lines_with_points(lines_df: ps.DataFrame, points_df: ps.DataFrame) -> ps.DataFrame:
    return (lines_df
            .join(points_df, on=ST_Intersects(lines_df.geometry, points_df.geometry), how='inner')
            .groupby(lines_df.geometry)
                .agg(
                    *(F.first(c).alias(get_column_name(c)) for c in all_columns_except_geometry(lines_df)),
                    F.collect_list(points_df.uuid).alias('points_uuid'),
                    F.collect_list(points_df.geometry).alias('points_geometry'),
                )
            )

def _add_arc(graph: nx.Graph, point1, point2, direction, data: dict):
    if direction == OneWay.Forward.value:
        graph.add_edge(point1, point2, **data)
    elif direction == OneWay.Backward.value:
        graph.add_edge(point2, point1, **data)
    else:
        graph.add_edge(point1, point2, **data)
        graph.add_edge(point2, point1, **data)


def _add_arcs(graph: nx.Graph, df: DataFrame) -> nx.Graph:
    for row in df.collect():
        points = row['points_uuid']
        point_geometry = row['points_geometry']

        if len(points) != 2:
            raise Exception(f"invalid number of points in line: {points}")
        if len(point_geometry) != 2:
            raise Exception(f"invalid number of points in line: {points}")

        direction = row[MandatoryColumns.oneway.value]
        if len(points) != 2:
            raise Exception(f"invalid number of points in line: {points}")

        point1, point2 = points if point_geometry[0].coords[0] == row['geometry'].coords[0] else points[::-1]
        _add_arc(graph, point1, point2, direction, {
            k: v for k, v in row.asDict().items() if k not in ['points_uuid', 'points_geometry', MandatoryColumns.oneway.value]
        })

    return graph

def reduce_graph(graph: nx.Graph) -> nx.Graph:
    while True:
        nodes_to_reduce = (n for n in graph.nodes() if graph.degree(n) == 2)

        for node in nodes_to_reduce:
            neighbors = list(graph.neighbors(node))
            edges = graph.edges(node, data=True)

            if len(neighbors) != 2 or len(edges) != 2:
                print("Riduzione:", node, graph.degree(node), edges, neighbors)
                continue

            n1, n2 = neighbors
            if n1 == n2 or graph.has_edge(n1, n2) or graph.has_edge(n2, n1):
                # skip to avoid multiple edges between same pair of nodes
                # which would require aggregation of edge attributes
               continue

            edge1, edge2 = edges

            edge1_data = graph.edges[node, n1]
            edge2_data = graph.edges[node, n2]

            merged_line = shapely.line_merge(shapely.MultiLineString([edge1_data['geometry'], edge2_data['geometry']]))
            coords = list(merged_line.coords)
            merged_data = {
                'geometry': shapely.LineString([shapely.geometry.Point(coords[0]), shapely.geometry.Point(coords[-1])]),
            }

            graph.remove_node(node)
            graph.add_edge(n1, n2, **merged_data)


    return reduced

def remove_nodes_without_edges(graph: nx.Graph) -> nx.Graph:
    graph.remove_nodes_from(n for n in graph.nodes() if graph.degree(n) == 0)
    return graph

def build_graph(roads_df: DataFrame,
                name: str = 'graph',
                joined_df: DataFrame | None = None,
                aggregate_functions: list[AggregationFunction] = None,
                buffer_radius_meters: float = 100,
                dataframe_only=False) -> nx.Graph | ps.DataFrame:
    """
    Build a directed graph from a DataFrame of roads.
    Optionally, enrich the graph with data from another DataFrame using spatial join and aggregation.
    By default, each edge of the graph is already enriched with distance information.

    Parameters
    ----------
    roads_df : DataFrame
        Road network as a DataFrame. Must contain at least columns of `MandatoryColumns` enumeration.
    name : str
        The name of the graph. Defaults to 'graph'.
    joined_df : DataFrame | None
        DataFrame to join with the roads DataFrame. If None, no join is performed. Defaults to None.
    aggregate_functions : list[AggregationFunction]
        List of aggregation functions to apply during the spatial aggregation after the join.
        If None, no aggregation is performed. Defaults to None.
        See also `AggregationFunction` and `spatial_aggregation` for more details.
    buffer_radius_meters : float
        The radius in meters to buffer the road segments before performing the spatial join.
        If joined_df is None, this parameter is ignored. Defaults to 100 meters.
    dataframe_only : bool
        If True, the function stops before building a networkx Graph and returns a Spark DataFrame instead.

    Returns
    -------
    nx.Graph | pyspark.sql.DataFrame
        The resulting directed graph as a networkx DiGraph or a Spark DataFrame if dataframe_only is True.
    """
    roads_df = to_spark_dataframe(roads_df)

    points_df = explode_multipoint_to_points(roads_df)
    segments_df = explode_multiline_to_lines(roads_df)

    del roads_df

    if joined_df is not None:
        buffered_df = (polygonize(segments_df, radius_meters=buffer_radius_meters)
                        .withColumnRenamed('geometry', 'road_geometry')
                        .withColumnRenamed('polygonized_geometry', 'geometry')
                        .withColumn('__join_id', F.monotonically_increasing_id())
                       )
        join_result = (spatial_join(buffered_df, joined_df, JoinType.INNER)
                       .withColumnRenamed('geometry_left', 'geometry')
                       )
        segments_df = (spatial_aggregation(join_result,
            group_by_column='__join_id',
            aggregate_functions=aggregate_functions if aggregate_functions else []
        ).drop('__join_id').drop('geometry').drop('geometry_right').withColumnRenamed('road_geometry', 'geometry'))

    lines_df = join_lines_with_points(segments_df, points_df)

    del segments_df
    del points_df

    if dataframe_only:
        return lines_df

    graph = _add_arcs(nx.DiGraph(), lines_df)
    del lines_df

    graph = remove_nodes_without_edges(graph)

    graph.name = name

    return graph


