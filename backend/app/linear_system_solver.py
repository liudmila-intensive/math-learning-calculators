from sympy import Matrix, Rational, latex, simplify


def parse_number(value):
    if value == "" or value is None:
        return Rational(0)
    return Rational(str(value).replace(",", "."))


def format_value(value):
    return str(simplify(value))


def matrix_latex(matrix):
    return latex(Matrix(matrix))


def augmented_latex(rows):
    return latex(Matrix(rows))


def determinant_latex(matrix):
    body = "\\\\".join("&".join(latex(simplify(value)) for value in row) for row in matrix)
    return f"\\begin{{vmatrix}}{body}\\end{{vmatrix}}"


def two_by_two_latex(matrix):
    return determinant_latex(matrix)


def equations_latex(coefficients, rhs):
    lines = []
    for row, value in zip(coefficients, rhs):
        terms = []
        for index, coef in enumerate(row, start=1):
            number = parse_number(coef)
            if number == 0:
                continue
            sign = "+" if number > 0 and terms else ""
            if number == 1:
                terms.append(f"{sign}x_{{{index}}}")
            elif number == -1:
                terms.append(f"-x_{{{index}}}")
            else:
                terms.append(f"{sign}{latex(number)}x_{{{index}}}")
        lines.append("".join(terms) + f"={latex(parse_number(value))}")
    return "\\begin{cases}" + "\\\\".join(lines) + "\\end{cases}"


def augmented_rows(a, b):
    return [[*row, b[index]] for index, row in enumerate(a)]


def row_sum(row):
    return simplify(sum(row))


ROW_NAMES = [
    "первую",
    "вторую",
    "третью",
    "четвертую",
    "пятую",
    "шестую",
]

ROW_NAMES_GENITIVE = [
    "первой",
    "второй",
    "третьей",
    "четвертой",
    "пятой",
    "шестой",
]


def row_name(index):
    if index < len(ROW_NAMES):
        return ROW_NAMES[index]
    return f"{index + 1}-ю"


def row_name_genitive(index):
    if index < len(ROW_NAMES_GENITIVE):
        return ROW_NAMES_GENITIVE[index]
    return f"{index + 1}-й"


def multiplier_text(value):
    value = simplify(value)
    if value == 1:
        return ""
    if value == 2:
        return "удвоенную "
    return f"умноженную на {format_value(value)} "


def operation_scale(row, multiplier):
    return f"{row_name(row).capitalize()} строку умножаем на {format_value(multiplier)}."


def operation_eliminate(target, pivot, pivot_value, factor):
    if pivot_value == 1:
        if factor > 0:
            return (
                f"Из {row_name_genitive(target)} строки вычитаем "
                f"{multiplier_text(factor)}{row_name(pivot)} строку."
            )
        return (
            f"К {row_name_genitive(target)} строке прибавляем "
            f"{multiplier_text(abs(factor))}{row_name(pivot)} строку."
        )
    if factor > 0:
        return (
            f"{row_name(target).capitalize()} строку умножаем на {format_value(pivot_value)} "
            f"и вычитаем {multiplier_text(factor)}{row_name(pivot)} строку."
        )
    return (
        f"{row_name(target).capitalize()} строку умножаем на {format_value(pivot_value)} "
        f"и прибавляем {multiplier_text(abs(factor))}{row_name(pivot)} строку."
    )


def build_table_state(rows, pivot=None, basis=None):
    table_rows = []
    n = len(rows[0]) - 1
    for row_index, row in enumerate(rows):
        table_rows.append({
            "basis": basis[row_index] if basis else "-",
            "values": [format_value(value) for value in row[:-1]],
            "rhs": format_value(row[-1]),
            "sum": format_value(row_sum(row)),
            "pivot_col": pivot[1] if pivot and pivot[0] == row_index else None,
        })
    return {"columns": [f"x_{index + 1}" for index in range(n)], "rows": table_rows}


def triangular_gauss(coefficients, rhs):
    a = [[parse_number(value) for value in row] for row in coefficients]
    b = [parse_number(value) for value in rhs]
    n = len(a)
    chain_steps = [{
        "operation": "",
        "latex": augmented_latex(augmented_rows(a, b)),
        "table": build_table_state(augmented_rows(a, b), pivot=(0, 0)),
    }]

    for col in range(n):
        pivot = None
        for row in range(col, n):
            if a[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            raise ValueError("Система не имеет единственного решения.")

        if pivot != col:
            before = augmented_latex(augmented_rows(a, b))
            a[col], a[pivot] = a[pivot], a[col]
            b[col], b[pivot] = b[pivot], b[col]
            chain_steps.append({
                "operation": f"Меняем местами {row_name(col)} и {row_name(pivot)} строки.",
                "before_latex": before,
                "latex": augmented_latex(augmented_rows(a, b)),
                "table": build_table_state(augmented_rows(a, b), pivot=(col, col)),
            })

        pivot_value = a[col][col]
        if abs(pivot_value) == 1 and pivot_value != 1:
            before = augmented_latex(augmented_rows(a, b))
            a[col] = [value * pivot_value for value in a[col]]
            b[col] = b[col] * pivot_value
            chain_steps.append({
                "operation": operation_scale(col, pivot_value),
                "before_latex": before,
                "latex": augmented_latex(augmented_rows(a, b)),
                "table": build_table_state(augmented_rows(a, b), pivot=(col, col)),
            })
            pivot_value = a[col][col]

        for row in range(col + 1, n):
            factor = a[row][col]
            if factor == 0:
                continue
            before = augmented_latex(augmented_rows(a, b))
            if pivot_value == 1:
                a[row] = [a[row][j] - factor * a[col][j] for j in range(n)]
                b[row] = b[row] - factor * b[col]
            else:
                a[row] = [pivot_value * a[row][j] - factor * a[col][j] for j in range(n)]
                b[row] = pivot_value * b[row] - factor * b[col]
            chain_steps.append({
                "operation": operation_eliminate(row, col, pivot_value, factor),
                "before_latex": before,
                "latex": augmented_latex(augmented_rows(a, b)),
                "table": build_table_state(augmented_rows(a, b), pivot=(row, col)),
            })

    solution = [Rational(0) for _ in range(n)]
    back_steps = []
    for row in range(n - 1, -1, -1):
        right = b[row] - sum(a[row][col] * solution[col] for col in range(row + 1, n))
        solution[row] = simplify(right / a[row][row])
        back_steps.append({
            "latex": f"x_{{{row + 1}}}=\\frac{{{latex(right)}}}{{{latex(a[row][row])}}}={latex(solution[row])}"
        })

    basis = [f"x_{index + 1}" for index in range(n)]
    final_rows = []
    for index, value in enumerate(solution):
        row = [Rational(0) for _ in range(n + 1)]
        row[index] = Rational(1)
        row[-1] = value
        final_rows.append(row)

    table_states = [step["table"] for step in chain_steps]
    table_states.append({
        "columns": [f"x_{index + 1}" for index in range(n)],
        "rows": build_table_state(final_rows, basis=basis)["rows"],
    })

    triangular_latex = equations_latex(
        [[format_value(value) for value in row] for row in a],
        [format_value(value) for value in b],
    )

    return {
        "chain_steps": chain_steps,
        "table_states": table_states,
        "triangular_latex": triangular_latex,
        "back_steps": back_steps,
        "solution": solution,
    }


def minor_matrix(matrix, skip_row, skip_col):
    return [
        [matrix[row][col] for col in range(len(matrix)) if col != skip_col]
        for row in range(len(matrix))
        if row != skip_row
    ]


def signed_term_latex(coef, sign, minor):
    prefix = "+" if sign == 1 else "-"
    if coef < 0 and sign == 1:
        prefix = "+"
    if coef < 0 and sign == -1:
        prefix = "-"
    return f"{prefix}{latex(abs(coef))}\\cdot{two_by_two_latex(minor)}"


def determinant_expansion_3(matrix):
    det_value = simplify(Matrix(matrix).det())
    minors = [minor_matrix(matrix, 0, col) for col in range(3)]
    signs = [1, -1, 1]
    symbolic_terms = []
    numeric_terms = []
    for col in range(3):
        coef = matrix[0][col]
        sign = signs[col]
        term_sign = sign if coef >= 0 else -sign
        symbolic_terms.append(signed_term_latex(coef, sign, minors[col]))
        minor_value = simplify(Matrix(minors[col]).det())
        numeric_terms.append(
            f"{'+' if term_sign > 0 else '-'}{latex(abs(coef))}\\cdot({latex(minor_value)})"
        )

    symbolic = "".join(symbolic_terms).lstrip("+")
    numeric = "".join(numeric_terms).lstrip("+")
    return {
        "matrix_latex": determinant_latex(matrix),
        "expansion_latex": f"{determinant_latex(matrix)}={symbolic}",
        "calculation_latex": f"{numeric}={latex(det_value)}",
        "value": format_value(det_value),
        "value_latex": latex(det_value),
    }


def build_cramer(a, b):
    n = len(a)
    det_a = simplify(Matrix(a).det())
    items = []
    for col in range(n):
        replaced = [row[:] for row in a]
        for row in range(n):
            replaced[row][col] = b[row]
        det_i = simplify(Matrix(replaced).det())
        item = {
            "index": col + 1,
            "matrix": [[format_value(value) for value in row] for row in replaced],
            "determinant": format_value(det_i),
            "determinant_latex": latex(det_i),
            "value": format_value(det_i / det_a),
            "value_latex": latex(det_i / det_a),
        }
        if n == 3:
            item["expansion"] = determinant_expansion_3(replaced)
        items.append(item)

    return {
        "determinant": format_value(det_a),
        "determinant_latex": latex(det_a),
        "expansion": determinant_expansion_3(a) if n == 3 else None,
        "items": items,
    }


def solve_linear_system(coefficients, rhs):
    if len(coefficients) != len(rhs):
        raise ValueError("Количество строк матрицы должно совпадать с количеством свободных членов.")
    if not coefficients or len(coefficients) != len(coefficients[0]):
        raise ValueError("Для этих методов нужна квадратная система n×n.")

    n = len(coefficients)
    if any(len(row) != n for row in coefficients):
        raise ValueError("Матрица коэффициентов должна быть квадратной.")

    a = [[parse_number(value) for value in row] for row in coefficients]
    b = [parse_number(value) for value in rhs]
    det_a = simplify(Matrix(a).det())
    if det_a == 0:
        raise ValueError("Определитель основной матрицы равен нулю, единственного решения нет.")

    gauss = triangular_gauss(coefficients, rhs)
    solution_values = gauss["solution"]
    solution = {f"x_{index + 1}": format_value(value) for index, value in enumerate(solution_values)}
    solution_latex = ";\\ ".join(
        f"x_{{{index + 1}}}={latex(value)}" for index, value in enumerate(solution_values)
    )

    return {
        "equations_latex": equations_latex(coefficients, rhs),
        "matrix_latex": matrix_latex(a),
        "rhs_latex": matrix_latex(b),
        "solution": solution,
        "solution_latex": solution_latex,
        "matrix_gauss": {
            "chain_steps": gauss["chain_steps"],
            "triangular_latex": gauss["triangular_latex"],
            "back_steps": gauss["back_steps"],
        },
        "table_gauss": {
            "states": gauss["table_states"],
        },
        "cramer": build_cramer(a, b),
    }
