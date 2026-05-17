from typing import List, Literal, Optional
from pydantic import BaseModel, Field


Relation = Literal["<=", ">=", "="]
ObjectiveType = Literal["max", "min"]


class ConstraintItem(BaseModel):
    coefficients: List[float]
    relation: Relation
    rhs: float


class LpSolveRequest(BaseModel):
    num_variables: int = Field(..., ge=1)
    num_constraints: int = Field(..., ge=1)
    objective_type: ObjectiveType
    objective: List[float]
    constraints: List[ConstraintItem]


class TableauStep(BaseModel):
    title: str
    description: str
    column_names: List[str]
    row_names: List[str]
    data: List[List[str]]
    pivot_row: Optional[int] = None
    pivot_col: Optional[int] = None
    pivot_element: Optional[str] = None


class LpSolveResponse(BaseModel):
    status: str
    message: str
    canonical_system: List[str]
    steps: List[TableauStep]
    solution: dict
    objective_value: Optional[str] = None