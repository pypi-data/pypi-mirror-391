import pytest
import pathlib
import pandas as pd
from libadalina_core.sedona_utils import EPSGFormats

from libadalina_analytics.relocation import RelocationResource
from libadalina_analytics.relocation import relocation_algorithm

SAMPLE_DIR = pathlib.Path(__file__).parent.parent / "samples"

@pytest.mark.parametrize("path,epsg,id_column,demand_column,resources", [
    (f"{SAMPLE_DIR}/relocation/PARABIAGO_unsat_epsg32632_wkt_AMELIA.csv",EPSGFormats.EPSG32632,'ID','popolazion', [
            RelocationResource(column_name='beds', amount=1.0),
            RelocationResource(column_name='personnel', amount=0.2)
        ])
])
def test_relocation_algorithm(path, epsg, id_column, demand_column, resources):
    relocation_df = pd.read_csv(path, sep=';')
    relocation_solution = relocation_algorithm(
        relocation_df,
        epsg=epsg,
        id_column=id_column,
        demand_column=demand_column,
        resources=resources
    )
    assert relocation_solution is not None
