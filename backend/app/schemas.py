from typing import List, Optional
from pydantic import BaseModel, Field


class SimplifyRequest(BaseModel):
    expression: str = Field(..., min_length=1, description="Алгебраическое выражение")
    substitute_variable: Optional[str] = None
    substitute_value: Optional[str] = None


class EquationRequest(BaseModel):
    equation: str = Field(..., min_length=1, description="Уравнение")
    variable: Optional[str] = None


class StepItem(BaseModel):
    expression: str
    explanation: str = ""
    latex: str = ""
    is_chain: bool = False


class SimplifyResponse(BaseModel):
    original: str
    result: str
    result_latex: str
    steps: List[StepItem]
    substitution: Optional[dict] = None
