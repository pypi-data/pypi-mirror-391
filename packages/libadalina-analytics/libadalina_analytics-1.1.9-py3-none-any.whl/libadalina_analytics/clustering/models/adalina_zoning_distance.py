from pydantic import BaseModel, Field, field_validator

_zoning_functions = ["euclidean", "manhattan", "chebyshev", "haversine", "hamming", "canberra", "braycurtis", "jaccard", "matching", "dice", "kulsinski", "rogerstanimoto", "russellrao", "sokalmichener", "sokalsneath"]

class ClusteringDistance(BaseModel):
    name: str = Field(description='Name of the column')
    """Name of the column in the input data to be used for distance calculation."""

    weight: int | None = Field(description='Weight of the column', default=1)
    """Weight of the distance in the overall distance calculation. Default is 1."""

    function: str | None = Field(description='Function used to compute the distance', default=None)
    """
    Distance function to use. Must be one of the following:
        - euclidean
        - manhattan
        - chebyshev
        - haversine
        - hamming
        - canberra
        - braycurtis
        - jaccard
        - matching
        - dice
        - kulsinski
        - rogerstanimoto
        - russellrao
        - sokalmichener
        - sokalsneath
    If None, the default function depends on the type of the values in the column:
        - geometric values default to scipy distance_matrix
        - float and int values default to euclidean
        - string values default to hamming
        - boolean values default to jaccard
    """

    @field_validator('function')
    def validate_func(cls, v):
        if v is not None and v not in _zoning_functions:
            raise ValueError(f'Function must be one of {_zoning_functions}')
        return v