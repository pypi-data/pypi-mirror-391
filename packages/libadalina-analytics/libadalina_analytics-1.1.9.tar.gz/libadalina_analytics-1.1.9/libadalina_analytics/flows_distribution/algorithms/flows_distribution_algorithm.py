import itertools
import math

import shapely
from libadalina_core.sedona_configuration import get_sedona_context
from libadalina_core.sedona_utils import DataFrame, to_spark_dataframe, DEFAULT_EPSG

from libadalina_analytics.flows_distribution.algorithms.origin_destination_extractor import get_shape_node
import networkx as nx
import dataclasses
import pandas as pd
import geopandas as gpd
import pyspark.sql as ps 
from pyspark.sql import functions as func
import gc

@dataclasses.dataclass
class GraphCost:
    name: str
    """The name of the cost attribute in the graph edges."""
    cost_per_unit: float
    """The cost per unit of the cost attribute."""
    weight: float
    """The weight of the cost attribute in the overall cost calculation. The sum of all weights must be equal to 1.0."""


def _compute_edge_cost(graph: nx.Graph, edge, edge_data, graph_costs: list[GraphCost]) -> float:
    cost = sum(
        edge_data.get(cost.name, 0) * cost.cost_per_unit * cost.weight for cost in graph_costs
    )
    graph.edges[edge]['__cost'] = cost
    return cost


def _compute_edges_cost(graph: nx.Graph, graph_costs: list[GraphCost]) -> None:
    for edge in graph.edges(data=True):
        _compute_edge_cost(graph, edge[0:2], edge[2], graph_costs)


def _get_source_and_destination_pairs(
        graph: nx.Graph,
        shapes_df: DataFrame,
        flows_df: DataFrame,
        shapes_id_column: str = 'id',
        flows_origin_id_column: str = 'origin_id',
        flows_destination_id_column: str = 'destination_id',
        sources: list = None,
        destinations: list = None
) -> ps.DataFrame:

    # filter flows DataFrame if sources or destinations are provided
    if sources is not None:
        flows_df = flows_df.filter(func.col(flows_origin_id_column).isin(sources))
    if destinations is not None:
        flows_df = flows_df.filter(func.col(flows_destination_id_column).isin(destinations))

    # filter out the flows from the same origin to the same destination
    flows_df = (flows_df
                .filter(func.col(flows_origin_id_column) != func.col(flows_destination_id_column)))

    shapes_df = to_spark_dataframe(shapes_df)
    if sources is not None or destinations is not None:
        sources_ids = (row[0] for row in flows_df.select(func.col(flows_origin_id_column)).distinct().collect())
        destination_ids = (row[0] for row in flows_df.select(func.col(flows_destination_id_column)).distinct().collect())

        shapes_df = shapes_df.filter(func.col(shapes_id_column).isin(list(set(
            itertools.chain(sources_ids, destination_ids)
        ))))
    shapes_node = get_shape_node(graph, shapes_df, shapes_id_column, [])

    # join with the tables to get the origin and destination graph nodes
    return (flows_df
                .join(shapes_node, func.col(flows_origin_id_column) == func.col(shapes_id_column), how='inner')
                .select(*(list(flows_df.columns)), func.col('closest_node').alias('origin_node'))
                .join(shapes_node, func.col(flows_destination_id_column) == func.col(shapes_id_column), how='inner')
                .select(*(list(flows_df.columns)), func.col('origin_node'),
                        func.col('closest_node').alias('destination_node'))
                )

def _compute_shortest_path(graph: nx.Graph, graph_costs: list[GraphCost], origin_id, destination_id, origin_node, destination_node):
    try:
        path = nx.astar_path(
            graph,
            source=origin_node,
            target=destination_node,
            weight='__cost'
        )
        unitary_cost = nx.path_weight(graph, path, weight='__cost')
        geometry = shapely.MultiLineString(
            [graph.get_edge_data(path[i], path[i + 1])['geometry'] for i in range(len(path) - 1)])
        return [origin_id, destination_id, path, geometry, unitary_cost] + [nx.path_weight(graph, path, weight=cost.name) for cost in graph_costs]
    except nx.NetworkXNoPath:
        return [origin_id, destination_id, [], shapely.Point(), math.inf] + [math.inf for _ in graph_costs]
    finally:
        gc.collect()

def flows_distribution_algorithm(
        graph: nx.Graph,
        shapes_df: DataFrame,
        flows_df: DataFrame,
        graph_costs: list[GraphCost],
        shapes_id_column: str = 'id',
        flows_origin_id_column: str = 'origin_id',
        flows_destination_id_column: str = 'destination_id',
        flows_demand_column: str = 'demand',
        sources: list = None,
        destinations: list = None
) -> ps.DataFrame | gpd.GeoDataFrame:
    """
    Distribute flow demands between origin and destination areas on a graph while minimizing total transportation costs.

    Parameters
    ----------
    graph : nx.Graph
        The networkx graph on which to distribute the flows. The graph edges must contain the cost attributes
        specified in `graph_costs`.
    shapes_df : pandas.DataFrame or geopandas.GeoDataFrame or pyspark.DataFrame
        A DataFrame containing the shapes of the areas with their geometries and identifiers.
    flows_df : pandas.DataFrame or geopandas.GeoDataFrame or pyspark.DataFrame
        A DataFrame containing the flows to distribute, with origin and destination identifiers and demand values.
    graph_costs : list[GraphCost]
        A list of GraphCost objects defining the cost attributes to consider in the graph edges, their cost per unit,
        and their weights in the overall cost calculation. The sum of all weights must be equal to 1.0.
    shapes_id_column : str
        The name of the column in `shapes_df` containing the area identifiers. Default is 'id'.
    flows_origin_id_column : str
        The name of the column in `flows_df` containing the origin area identifiers. Default is 'origin_id'.
    flows_destination_id_column : str
        The name of the column in `flows_df` containing the destination area identifiers. Default is 'destination_id'.
    flows_demand_column : str
        The name of the column in `flows_df` containing the demand values to distribute. Default is 'demand'.
    sources : list | None
        An optional list of origin area identifiers to filter the flows. If provided, only flows with origins in this
        list will be considered. Default is None.
        Identifiers must be of the same type as the ones in `flows_origin_id_column`.
    destinations : list | None
        An optional list of destination area identifiers to filter the flows. If provided, only flows with destinations
        in this list will be considered. Default is None.
        Identifiers must be of the same type as the ones in `flows_destination_id_column`.

    Returns
    -------
    pandas.DataFrame or geopandas.GeoDataFrame or pyspark.DataFrame
        The DataFrame flows_df enriched with columns for the computed path, its geometry,
        the total path cost, and the individual costs for each pair or origin and destination areas.
        If the input `flows_df` is a pandas DataFrame or a geopandas GeoDataFrame, the output will be a geopandas
        GeoDataFrame, otherwise a pyspark DataFrame.
    """
    if sum(cost.weight for cost in graph_costs) != 1.0:
        raise ValueError("The sum of the weights of the graph costs must be equal to 1.0")

    flows_df_type = type(flows_df)

    if isinstance(flows_df, pd.DataFrame) or isinstance(flows_df, gpd.GeoDataFrame):
        flows_df = get_sedona_context().createDataFrame(flows_df)

    source_and_destination_pairs = _get_source_and_destination_pairs(
        graph, shapes_df, flows_df,
        shapes_id_column, flows_origin_id_column, flows_destination_id_column,
        sources, destinations
    ).select(flows_origin_id_column, flows_destination_id_column, 'origin_node',
                                        'destination_node').distinct()

    _compute_edges_cost(graph, graph_costs)

    source_and_destination_pairs = source_and_destination_pairs.collect()
    if not source_and_destination_pairs or len(source_and_destination_pairs) == 0:
        if sources is not None or destinations is not None:
            raise ValueError(f"Could not find any pair of source and destination on the graph. Sources {sources} - Destinations {destinations}.")
        else:
            raise ValueError(f"Could not find any pair of source and destination on the graph.")

    paths_df = get_sedona_context().createDataFrame(
        (_compute_shortest_path(graph, graph_costs,
                               row[flows_origin_id_column], row[flows_destination_id_column],
                               row['origin_node'], row['destination_node']
                               ) for row in source_and_destination_pairs),
        [flows_origin_id_column, flows_destination_id_column, 'path', 'geometry', 'path_cost'] +
        [cost.name for cost in graph_costs]
    )
    flows_df = (flows_df
                .join(paths_df, [flows_origin_id_column, flows_destination_id_column], how='inner')
                .withColumn('path_cost', func.col('path_cost') * func.col(flows_demand_column))
                )

    if flows_df_type is pd.DataFrame:
        return gpd.GeoDataFrame(flows_df.toPandas(), geometry = 'geometry', crs = DEFAULT_EPSG.value)
    else:
        return flows_df