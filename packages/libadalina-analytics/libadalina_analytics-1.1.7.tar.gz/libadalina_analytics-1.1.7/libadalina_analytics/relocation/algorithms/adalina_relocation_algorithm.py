from libadalina_core.sedona_utils import DataFrame, EPSGFormats
from libadalina_analytics.utils import GeometryFormats
from .adalina_algorithms import run_hierarchy_with_distance_threshold
from ..models import AdalinaData, AdalinaSolution, AdalinaAlgorithmOptions
from ..models.adalina_solution import get_solution_csv_AMELIA
import pandas as pd

from ..models.relocation_resource import RelocationResource


def relocation_algorithm(data: DataFrame,
                         epsg: EPSGFormats,
                         id_column: str = 'id',
                         geometry_column: str = 'geometry',
                         demand_column: str = 'demand',
                         geometry_format: GeometryFormats = GeometryFormats.WKT,
                         max_distance_assignment: float | None = None,
                         max_distance_relocation: float | None = None,
                         server_column: str | None = None,
                         resources: list[RelocationResource] | None = None,
                         timelimit: int = 60) -> pd.DataFrame | None:
    """
    Optimally assign demand to servers minimizing relocation costs.

    Parameters
    ----------
    data : pandas.DataFrame
        The input data containing the geometries and properties.
    epsg : EPSGFormats
        The EPSG format of the input geometries.
    id_column : str
        The name of the column containing the unique identifiers for each location. Default is 'id'.
    geometry_column : str
        The name of the column containing the geometries. Default is 'geometry'.
    demand_column : str
        The name of the column containing the demand values. Default is 'demand'.
    geometry_format : GeometryFormats
        The format of the geometries in the geometry column. Default is GeometryFormats.WKT.
    max_distance_assignment : float | None
        The maximum distance allowed for assigning demand to servers. If None, no limit is applied. Default is None.
    max_distance_relocation : float | None
        The maximum distance allowed for relocating demands. If None, no limit is applied. Default is None.
    server_column : str | None
        The name of the column indicating whether a location is a server (True) or not (False).
        If None, all locations are considered as potential servers. Default is None.
    resources : list[RelocationResource] | None
        A list of RelocationResource objects representing the resources available at each server.
        Each RelocationResource contains:
            - column_name: The name of the column in the input data representing the resource
            - amount: The total amount of the resource needed to serve one unit of demand.
    timelimit : int
        The maximum time (in seconds) to run the algorithm. Default is 60 seconds.

    Returns
    -------
    pandas.DataFrame | None
        A DataFrame containing the optimal assignment of demand to servers, or None if no solution is found.
    """
    user_input: dict = {
        "epsg": epsg,
        "geometry_type": geometry_format,
        "geometry": geometry_column,
        "timelimit": timelimit
    }
    if id_column is not None:
        user_input["IDs"] = id_column
    if max_distance_assignment is not None:
        user_input["max_distance_assignment"] = max_distance_assignment
    if max_distance_relocation is not None:
        user_input["max_distance_relocation"] = max_distance_relocation
    if demand_column is not None:
        user_input["demand"] = demand_column
    if resources is not None:
        user_input["resources"] = [{
            'name': resource.column_name,
            'amount': resource.amount
        } for resource in resources]
    if server_column is not None:
        user_input["is_server"] = server_column

    data = AdalinaData.from_Amelia(amelia_file=data,
                                   user_input=user_input
                                   )

    # 4 - RUN ADALINA HIERARCHICAL ALGORITHM
    options = AdalinaAlgorithmOptions()  # I keep the default options
    _, all_solutions = run_hierarchy_with_distance_threshold(data, options)

    if len(all_solutions) == 0:
        return None

    return get_solution_csv_AMELIA(all_solutions[-1], data, epsg, geometry_format)
