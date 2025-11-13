from pydantic import BaseModel


class RelocationResource(BaseModel):
    column_name: str
    """Name of the column in the input data representing the resource."""
    amount: float
    """Amount of the resource needed to serve one unit of demand."""
