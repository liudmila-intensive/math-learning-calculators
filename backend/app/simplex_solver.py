from fractions import Fraction


def fr(value):
    return Fraction(str(value)).limit_denominator()


def fmt(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def var_name(index: int) -> str:
    return f"x_{index}"


def term_to_str(coef: Fraction, name: str, first: bool = False) -> str:
    if coef == 0:
        return ""

    if coef > 0:
        sign = "" if first else "+"
        abs_coef = coef
    else:
        sign = "-"
        abs_coef = -coef

    if abs_coef == 1:
        return f"{sign}{name}"
    return f"{sign}{fmt(abs_coef)}{name}"


def terms_to_str(terms):
    parts = []
    first = True
    for coef, name in terms:
        text = term_to_str(coef, name, first)
        if text:
            parts.append(text)
            first = False
    return "".join(parts) if parts else "0"


def ratio_label(value):
    if value is None:
        return "∞"
    return fmt(value)


class SimplexSolver:
    def __init__(self, num_variables, objective, constraints, objective_type="max"):
        self.n = num_variables
        self.objective_type = objective_type
        self.original_objective = [fr(x) for x in objective]
        self.objective = [fr(x) for x in objective]
        if objective_type == "min":
            self.objective = [-x for x in self.objective]
        self.constraints = constraints
        self.steps = []

    def build_canonical_system(self):
        canonical_system = []
        basis_expressions = []

        for i, constraint in enumerate(self.constraints):
            coeffs = [fr(x) for x in constraint["coefficients"]]
            relation = constraint["relation"]
            rhs = fr(constraint["rhs"])
            slack = var_name(self.n + i + 1)

            left_terms = [(coef, var_name(j + 1)) for j, coef in enumerate(coeffs)]
            if relation == "<=":
                left_terms.append((Fraction(1), slack))
            elif relation == ">=":
                left_terms.append((Fraction(-1), slack))
            elif relation != "=":
                raise ValueError(f"Неизвестный знак ограничения: {relation}")

            canonical_system.append(f"{terms_to_str(left_terms)}={fmt(rhs)}")

            if relation == "<=":
                basis_terms = [(coef, var_name(j + 1)) for j, coef in enumerate(coeffs)]
                basis_expressions.append(f"{slack}={fmt(rhs)}-({terms_to_str(basis_terms)})")
            elif relation == ">=":
                basis_terms = [(-coef, var_name(j + 1)) for j, coef in enumerate(coeffs)]
                basis_expressions.append(f"{slack}={fmt(-rhs)}-({terms_to_str(basis_terms)})")

        objective_terms = [(-coef, var_name(j + 1)) for j, coef in enumerate(self.objective)]
        objective_expression = f"F=0-({terms_to_str(objective_terms)})"

        return canonical_system, basis_expressions, objective_expression

    def build_initial_table(self):
        free_names = [var_name(i + 1) for i in range(self.n)]
        basis_names = []
        rhs_values = []
        rows_values = []

        for i, constraint in enumerate(self.constraints):
            coeffs = [fr(x) for x in constraint["coefficients"]]
            relation = constraint["relation"]
            rhs = fr(constraint["rhs"])
            basis_names.append(var_name(self.n + i + 1))

            if relation == "<=":
                rhs_values.append(rhs)
                rows_values.append(coeffs)
            elif relation == ">=":
                rhs_values.append(-rhs)
                rows_values.append([-coef for coef in coeffs])
            elif relation == "=":
                rhs_values.append(rhs)
                rows_values.append(coeffs)
            else:
                raise ValueError(f"Неизвестный знак ограничения: {relation}")

        basis_names.append("F")
        rhs_values.append(Fraction(0))
        rows_values.append([-coef for coef in self.objective])

        return basis_names, free_names, rhs_values, rows_values

    def choose_pivot_col(self, objective_row):
        candidates = [(abs(value), index) for index, value in enumerate(objective_row) if value < 0]
        if not candidates:
            return None
        return max(candidates)[1]

    def ratio_values(self, rhs_values, rows_values, pivot_col):
        ratios = []
        for i in range(len(rows_values) - 1):
            b = rhs_values[i]
            a = rows_values[i][pivot_col]
            if a == 0:
                ratios.append(None)
                continue

            value = b / a
            ratios.append(abs(value) if value > 0 else None)
        return ratios

    def choose_pivot_row(self, rhs_values, rows_values, pivot_col):
        ratios = self.ratio_values(rhs_values, rows_values, pivot_col)
        finite = [(value, index) for index, value in enumerate(ratios) if value is not None]
        if not finite:
            return None
        return min(finite)[1]

    def describe_table(self, basis_names, free_names, rhs_values, rows_values, pivot_col, pivot_row):
        if pivot_col is None:
            return (
                "В индексной строке нет отрицательных коэффициентов. "
                "Следовательно, полученное решение оптимально."
            )

        objective_row = rows_values[-1]
        negative_terms = [
            f"|{fmt(value)}|"
            for value in objective_row
            if value < 0
        ]
        pivot_var = free_names[pivot_col]
        ratios = self.ratio_values(rhs_values, rows_values, pivot_col)
        ratio_text = ", ".join(ratio_label(value) for value in ratios)

        if pivot_row is None:
            return (
                f"В индексной строке есть отрицательные коэффициенты: {', '.join(negative_terms)}. "
                f"Ведущий столбец - {pivot_var}. Допустимая ведущая строка отсутствует."
            )

        return (
            f"В индексной строке есть отрицательные коэффициенты: {', '.join(negative_terms)}. "
            f"Ведущий столбец - {pivot_var}. "
            f"Отношения свободных членов к элементам ведущего столбца: min{{{ratio_text}}} = "
            f"{ratio_label(ratios[pivot_row])}. "
            f"Ведущая строка - {basis_names[pivot_row]}, ведущий элемент - "
            f"{fmt(rows_values[pivot_row][pivot_col])}."
        )

    def save_table(self, title, basis_names, free_names, rhs_values, rows_values, pivot_col=None, pivot_row=None):
        data = []
        for row, rhs in zip(rows_values, rhs_values):
            data.append([fmt(value) for value in row] + [fmt(rhs)])

        pivot_element = None
        if pivot_col is not None and pivot_row is not None:
            pivot_element = rows_values[pivot_row][pivot_col]

        self.steps.append({
            "title": title,
            "description": self.describe_table(
                basis_names,
                free_names,
                rhs_values,
                rows_values,
                pivot_col,
                pivot_row,
            ),
            "column_names": free_names + ["b"],
            "row_names": basis_names,
            "data": data,
            "pivot_row": pivot_row,
            "pivot_col": pivot_col,
            "pivot_element": fmt(pivot_element) if pivot_element is not None else None,
        })

    def build_next_table(self, basis_names, free_names, rhs_values, rows_values, pivot_row, pivot_col):
        old_basis = basis_names[:]
        old_free = free_names[:]
        old_rhs = rhs_values[:]
        old_rows = [row[:] for row in rows_values]

        pivot = old_rows[pivot_row][pivot_col]
        if pivot == 0:
            raise ValueError("Ведущий элемент равен нулю")

        new_basis = old_basis[:]
        new_free = old_free[:]
        entering = old_free[pivot_col]
        leaving = old_basis[pivot_row]
        new_basis[pivot_row] = entering
        new_free[pivot_col] = leaving

        row_count = len(old_rows)
        col_count = len(old_rows[0])
        new_rhs = [Fraction(0) for _ in range(row_count)]
        new_rows = [[Fraction(0) for _ in range(col_count)] for _ in range(row_count)]

        new_rhs[pivot_row] = old_rhs[pivot_row] / pivot
        for j in range(col_count):
            if j == pivot_col:
                new_rows[pivot_row][j] = Fraction(1) / pivot
            else:
                new_rows[pivot_row][j] = old_rows[pivot_row][j] / pivot

        for i in range(row_count):
            if i == pivot_row:
                continue

            helper = -old_rows[i][pivot_col]
            new_rhs[i] = new_rhs[pivot_row] * helper + old_rhs[i]

            for j in range(col_count):
                if j == pivot_col:
                    new_rows[i][j] = new_rows[pivot_row][j] * helper
                else:
                    new_rows[i][j] = new_rows[pivot_row][j] * helper + old_rows[i][j]

        return new_basis, new_free, new_rhs, new_rows

    def current_solution(self, basis_names, rhs_values):
        solution = {var_name(i + 1): "0" for i in range(self.n)}

        for i, name in enumerate(basis_names[:-1]):
            if name.startswith("x_"):
                index = int(name.split("_")[1])
                if index <= self.n:
                    solution[name] = fmt(rhs_values[i])

        return solution

    def response_base(self, canonical_system, basis_expressions, objective_expression, initial_table):
        initial_basis, initial_free, initial_rhs, initial_rows = initial_table
        return {
            "canonical_system": canonical_system,
            "basis_expressions": basis_expressions,
            "objective_expression": objective_expression,
            "initial_sample_table": {
                "basis_names": initial_basis,
                "rhs": [fmt(value) for value in initial_rhs],
                "free_var_names": initial_free,
                "rows": [[fmt(value) for value in row] for row in initial_rows],
            },
        }

    def solve(self):
        canonical_system, basis_expressions, objective_expression = self.build_canonical_system()
        initial_table = self.build_initial_table()

        basis_names, free_names, rhs_values, rows_values = (
            initial_table[0][:],
            initial_table[1][:],
            initial_table[2][:],
            [row[:] for row in initial_table[3]],
        )

        max_iterations = 50
        table_number = 1

        while table_number <= max_iterations:
            pivot_col = self.choose_pivot_col(rows_values[-1])

            if pivot_col is None:
                self.save_table(
                    f"Таблица {table_number}",
                    basis_names,
                    free_names,
                    rhs_values,
                    rows_values,
                )

                objective_value = rhs_values[-1]
                if self.objective_type == "min":
                    objective_value = -objective_value

                return {
                    "status": "optimal",
                    "message": "Оптимальное решение найдено.",
                    **self.response_base(
                        canonical_system,
                        basis_expressions,
                        objective_expression,
                        initial_table,
                    ),
                    "steps": self.steps,
                    "solution": self.current_solution(basis_names, rhs_values),
                    "objective_value": fmt(objective_value),
                }

            pivot_row = self.choose_pivot_row(rhs_values, rows_values, pivot_col)
            self.save_table(
                f"Таблица {table_number}",
                basis_names,
                free_names,
                rhs_values,
                rows_values,
                pivot_col,
                pivot_row,
            )

            if pivot_row is None:
                return {
                    "status": "unbounded",
                    "message": "Допустимая ведущая строка отсутствует.",
                    **self.response_base(
                        canonical_system,
                        basis_expressions,
                        objective_expression,
                        initial_table,
                    ),
                    "steps": self.steps,
                    "solution": {},
                    "objective_value": None,
                }

            basis_names, free_names, rhs_values, rows_values = self.build_next_table(
                basis_names,
                free_names,
                rhs_values,
                rows_values,
                pivot_row,
                pivot_col,
            )

            table_number += 1

        raise ValueError("Превышено максимальное число итераций")
