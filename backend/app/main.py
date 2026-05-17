import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.schemas import EquationRequest, SimplifyRequest, SimplifyResponse
from app.algebra import build_simplify_steps, evaluate_expression
from app.equation_solver import build_equation_steps
from app.simplex_solver import SimplexSolver
from app.simplex_algebraic_solver import SimplexAlgebraicSolver
from app.transport_solver import TransportSolver
from app.linear_system_solver import solve_linear_system
from app.export_builders import (
    build_simplify_docx,
    build_equation_docx,
    build_simplex_docx,
    build_simplex_algebraic_docx,
    build_transport_docx,
)

app = FastAPI(
    title="School Calculators API",
    version="1.0.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
frontend_origin = os.getenv("FRONTEND_ORIGIN")
if frontend_origin:
    origins.append(frontend_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "API is running"}


@app.post("/simplify", response_model=SimplifyResponse)
def simplify_expression(payload: SimplifyRequest):
    try:
        original, result, result_latex, steps = build_simplify_steps(payload.expression)
        substitution = None
        if payload.substitute_variable and payload.substitute_value:
            substitution = evaluate_expression(
                payload.expression,
                payload.substitute_variable,
                payload.substitute_value,
            )
        return {
            "original": original,
            "result": result,
            "result_latex": result_latex,
            "steps": steps,
            "substitution": substitution,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка обработки выражения: {str(e)}"
        )


@app.post("/equation")
def solve_equation(payload: EquationRequest):
    try:
        return build_equation_steps(payload.equation, payload.variable)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка решения уравнения: {str(e)}"
        )


@app.post("/simplex")
def solve_simplex(data: dict):
    try:
        print("=== simplex request received ===")
        print(data)

        solver = SimplexSolver(
            num_variables=data["num_variables"],
            objective=data["objective"],
            constraints=data["constraints"],
            objective_type=data.get("objective_type", "max"),
        )

        result = solver.solve()

        print("=== simplex finished ===")
        print(result)

        return result
    except Exception as e:
        print("=== simplex error ===")
        print(str(e))
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка решения задачи: {str(e)}"
        )


@app.post("/simplex-algebraic")
def solve_simplex_algebraic(data: dict):
    try:
        solver = SimplexAlgebraicSolver(
            num_variables=data["num_variables"],
            objective=data["objective"],
            constraints=data["constraints"],
            objective_type=data.get("objective_type", "max"),
        )
        return solver.solve()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка решения задачи: {str(e)}"
        )


@app.post("/transport")
def solve_transport(data: dict):
    try:
        solver = TransportSolver(
            costs=data["costs"],
            supply=data["supply"],
            demand=data["demand"],
        )
        return solver.solve()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка решения задачи: {str(e)}"
        )


@app.post("/linear-system")
def solve_linear_system_endpoint(data: dict):
    try:
        return solve_linear_system(data["coefficients"], data["rhs"])
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка решения системы: {str(e)}"
        )


def docx_response(buffer, filename):
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@app.post("/simplify/docx")
def export_simplify_docx(data: dict):
    try:
        return docx_response(build_simplify_docx(data), "simplify_solution.docx")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка формирования файла: {str(e)}")


@app.post("/equation/docx")
def export_equation_docx(data: dict):
    try:
        return docx_response(build_equation_docx(data), "equation_solution.docx")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка формирования файла: {str(e)}")


@app.post("/simplex/docx")
def export_simplex_docx(data: dict):
    try:
        return docx_response(build_simplex_docx(data), "simplex_solution.docx")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка формирования файла: {str(e)}")


@app.post("/simplex-algebraic/docx")
def export_simplex_algebraic_docx(data: dict):
    try:
        return docx_response(build_simplex_algebraic_docx(data), "simplex_algebraic_solution.docx")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка формирования файла: {str(e)}")


@app.post("/transport/docx")
def export_transport_docx(data: dict):
    try:
        return docx_response(build_transport_docx(data), "transport_solution.docx")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка формирования файла: {str(e)}")
