from app.algebra import build_simplify_steps, evaluate_expression
from app.docx_export import make_docx
from app.equation_solver import build_equation_steps
from app.simplex_algebraic_solver import SimplexAlgebraicSolver
from app.simplex_solver import SimplexSolver
from app.transport_solver import TransportSolver


def simplex_condition(data):
    rows = [["Ограничение", "Знак", "b"]]
    for item in data["constraints"]:
        left = " + ".join(
            f"{coef}x_{index + 1}"
            for index, coef in enumerate(item["coefficients"])
        )
        rows.append([left, item["relation"], item["rhs"]])
    return rows


def build_simplify_docx(data):
    original, result, _, steps = build_simplify_steps(data["expression"])
    blocks = [
        {"type": "heading", "text": "Упрощение выражения"},
        {"type": "paragraph", "text": f"Условие: {original}"},
        {"type": "heading", "text": "Ход решения"},
    ]
    for step in steps:
        blocks.append({"type": "paragraph", "text": f"{step.get('title', '')}: {step.get('expression', '')}"})
        if step.get("explanation"):
            blocks.append({"type": "paragraph", "text": step["explanation"]})
    if data.get("substitute_variable") and data.get("substitute_value"):
        substitution = evaluate_expression(
            data["expression"],
            data["substitute_variable"],
            data["substitute_value"],
        )
        blocks.append({"type": "heading", "text": "Подстановка значения"})
        blocks.append({
            "type": "paragraph",
            "text": (
                f"При {substitution['variable']}={substitution['value']}: "
                f"{substitution['expression']}={substitution['result']}"
            ),
        })
    blocks += [
        {"type": "heading", "text": "Ответ"},
        {"type": "paragraph", "text": result},
    ]
    return make_docx(blocks)


def build_equation_docx(data):
    result = build_equation_steps(data["equation"], data.get("variable"))
    blocks = [
        {"type": "heading", "text": "Решение уравнения"},
        {"type": "paragraph", "text": f"Условие: {result['original']}"},
        {"type": "heading", "text": "Ход решения"},
    ]
    for step in result["steps"]:
        blocks.append({"type": "paragraph", "text": step.get("expression", "")})
        if step.get("explanation"):
            blocks.append({"type": "paragraph", "text": step["explanation"]})
    blocks += [
        {"type": "heading", "text": "Ответ"},
        {"type": "paragraph", "text": result["result"]},
    ]
    return make_docx(blocks)


def build_simplex_docx(data):
    result = SimplexSolver(
        data["num_variables"],
        data["objective"],
        data["constraints"],
        data.get("objective_type", "max"),
    ).solve()

    blocks = [
        {"type": "heading", "text": "Симплекс-метод"},
        {"type": "paragraph", "text": f"Целевая функция: {data['objective']} -> {data.get('objective_type', 'max')}"},
        {"type": "table", "rows": simplex_condition(data)},
        {"type": "heading", "text": "Каноническая форма"},
    ]
    for line in result.get("canonical_system", []):
        blocks.append({"type": "paragraph", "text": line})

    blocks.append({"type": "heading", "text": "Симплекс-таблицы"})
    for step in result.get("steps", []):
        blocks.append({"type": "heading", "text": step["title"]})
        blocks.append({"type": "paragraph", "text": step.get("description", "")})
        rows = [["Базис"] + step["column_names"]]
        rows += [[name] + row for name, row in zip(step["row_names"], step["data"])]
        blocks.append({"type": "table", "rows": rows})

    blocks += [
        {"type": "heading", "text": "Ответ"},
        {"type": "paragraph", "text": f"Решение: {result.get('solution', {})}"},
        {"type": "paragraph", "text": f"Значение целевой функции: {result.get('objective_value')}"},
    ]
    return make_docx(blocks)


def build_simplex_algebraic_docx(data):
    result = SimplexAlgebraicSolver(
        data["num_variables"],
        data["objective"],
        data["constraints"],
        data.get("objective_type", "max"),
    ).solve()

    blocks = [
        {"type": "heading", "text": "Симплекс-метод с алгебраическими преобразованиями"},
        {"type": "paragraph", "text": f"Целевая функция: {data['objective']} -> {data.get('objective_type', 'max')}"},
        {"type": "table", "rows": simplex_condition(data)},
        {"type": "heading", "text": "Ход решения"},
    ]
    for step in result.get("steps", []):
        blocks.append({"type": "heading", "text": step["title"]})
        blocks.append({"type": "paragraph", "text": step.get("description", "")})
        blocks.append({"type": "paragraph", "text": f"Основные переменные: {', '.join(step['basis'])}"})
        blocks.append({"type": "paragraph", "text": f"Неосновные переменные: {', '.join(step['free'])}"})
        for line in step.get("equations", []):
            blocks.append({"type": "paragraph", "text": line})
        blocks.append({"type": "paragraph", "text": step.get("objective_expression", "")})

    blocks += [
        {"type": "heading", "text": "Ответ"},
        {"type": "paragraph", "text": f"Решение: {result.get('solution', {})}"},
        {"type": "paragraph", "text": f"Значение целевой функции: {result.get('objective_value')}"},
    ]
    return make_docx(blocks)


def build_transport_docx(data):
    result = TransportSolver(data["costs"], data["supply"], data["demand"]).solve()
    blocks = [
        {"type": "heading", "text": "Транспортная задача"},
        {"type": "heading", "text": "Условие"},
    ]
    input_rows = [["Поставщик"] + [f"B_{i + 1}" for i in range(len(data["demand"]))] + ["Запас"]]
    for i, row in enumerate(data["costs"]):
        input_rows.append([f"A_{i + 1}"] + row + [data["supply"][i]])
    input_rows.append(["Потребность"] + data["demand"] + [""])
    blocks.append({"type": "table", "rows": input_rows})

    for step in result.get("steps", []):
        blocks.append({"type": "heading", "text": step["title"]})
        blocks.append({"type": "paragraph", "text": step.get("note", "")})
        rows = [["Поставщик"] + [f"B_{i + 1}" for i in range(len(step["demand"]))] + ["Запас"]]
        for i, row in enumerate(step["plan"]):
            rows.append([f"A_{i + 1}"] + row + [step["supply"][i]])
        rows.append(["Потребность"] + step["demand"] + [""])
        blocks.append({"type": "table", "rows": rows})
        if step.get("estimates"):
            blocks.append({"type": "paragraph", "text": "Оценки свободных клеток:"})
            for item in step["estimates"]:
                blocks.append({"type": "paragraph", "text": f"{item['cell']}: {item['text']}"})
        blocks.append({"type": "paragraph", "text": f"Стоимость: {step['cost_formula']} ден. ед."})

    blocks += [
        {"type": "heading", "text": "Ответ"},
        {"type": "paragraph", "text": f"Smin = {result.get('total_cost')} ден. ед."},
    ]
    return make_docx(blocks)
