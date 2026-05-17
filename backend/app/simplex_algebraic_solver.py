from fractions import Fraction

from app.simplex_solver import fr, fmt, var_name


def signed_term(coef: Fraction, name: str, first=False) -> str:
    if coef == 0:
        return ""

    if coef > 0:
        sign = "" if first else "+"
        value = coef
    else:
        sign = "-"
        value = -coef

    if value == 1:
        return f"{sign}{name}"
    return f"{sign}{fmt(value)}{name}"


def expression_text(name, rhs, coeffs, free_names):
    parts = [f"{name}={fmt(rhs)}"]
    for coef, free_name in zip(coeffs, free_names):
        text = signed_term(-coef, free_name)
        if text:
            parts.append(text)
    return "".join(parts)


def objective_text(constant, coeffs, free_names):
    parts = [f"F={fmt(constant)}"]
    for coef, free_name in zip(coeffs, free_names):
        text = signed_term(coef, free_name)
        if text:
            parts.append(text)
    return "".join(parts)


def ratio_label(value):
    return "∞" if value is None else fmt(value)


class SimplexAlgebraicSolver:
    def __init__(self, num_variables, objective, constraints, objective_type="max"):
        self.n = num_variables
        self.objective_type = objective_type
        self.objective = [fr(x) for x in objective]
        if objective_type == "min":
            self.objective = [-x for x in self.objective]
        self.constraints = constraints
        self.steps = []

    def build_initial(self):
        basis = []
        free = [var_name(i + 1) for i in range(self.n)]
        rhs = []
        rows = []
        canonical = []

        for i, constraint in enumerate(self.constraints):
            coeffs = [fr(x) for x in constraint["coefficients"]]
            relation = constraint["relation"]
            value = fr(constraint["rhs"])
            slack = var_name(self.n + i + 1)
            basis.append(slack)

            left = []
            for j, coef in enumerate(coeffs):
                text = signed_term(coef, var_name(j + 1), first=not left)
                if text:
                    left.append(text)

            if relation == "<=":
                left.append(signed_term(Fraction(1), slack, first=not left))
                rhs.append(value)
                rows.append(coeffs)
            elif relation == ">=":
                left.append(signed_term(Fraction(-1), slack, first=not left))
                rhs.append(-value)
                rows.append([-coef for coef in coeffs])
            else:
                raise ValueError("Метод поддерживает ограничения со знаками <= и >=")

            canonical.append(f"{''.join(left)}={fmt(value)}")

        return basis, free, rhs, rows, canonical

    def basic_solution(self, basis, rhs):
        result = {var_name(i + 1): "0" for i in range(self.n + len(self.constraints))}
        for name, value in zip(basis, rhs):
            result[name] = fmt(value)
        return result

    def objective_expression(self, basis, free, rhs, rows):
        constant = Fraction(0)
        coeffs = [Fraction(0) for _ in free]

        for i in range(self.n):
            name = var_name(i + 1)
            obj_coef = self.objective[i]

            if name in basis:
                row_index = basis.index(name)
                constant += obj_coef * rhs[row_index]
                for j, row_coef in enumerate(rows[row_index]):
                    coeffs[j] += obj_coef * (-row_coef)
            elif name in free:
                coeffs[free.index(name)] += obj_coef

        return constant, coeffs

    def equations(self, basis, free, rhs, rows):
        return [
            expression_text(name, value, row, free)
            for name, value, row in zip(basis, rhs, rows)
        ]

    def pivot(self, basis, free, rhs, rows, pivot_row, pivot_col):
        pivot_value = rows[pivot_row][pivot_col]
        if pivot_value == 0:
            raise ValueError("Ведущий элемент равен нулю")

        new_basis = basis[:]
        new_free = free[:]
        entering = free[pivot_col]
        leaving = basis[pivot_row]
        new_basis[pivot_row] = entering
        new_free[pivot_col] = leaving

        row_count = len(rows)
        col_count = len(rows[0])
        new_rhs = [Fraction(0) for _ in range(row_count)]
        new_rows = [[Fraction(0) for _ in range(col_count)] for _ in range(row_count)]

        new_rhs[pivot_row] = rhs[pivot_row] / pivot_value
        for j in range(col_count):
            if j == pivot_col:
                new_rows[pivot_row][j] = Fraction(1) / pivot_value
            else:
                new_rows[pivot_row][j] = rows[pivot_row][j] / pivot_value

        for i in range(row_count):
            if i == pivot_row:
                continue

            helper = -rows[i][pivot_col]
            new_rhs[i] = new_rhs[pivot_row] * helper + rhs[i]
            for j in range(col_count):
                if j == pivot_col:
                    new_rows[i][j] = new_rows[pivot_row][j] * helper
                else:
                    new_rows[i][j] = new_rows[pivot_row][j] * helper + rows[i][j]

        return new_basis, new_free, new_rhs, new_rows

    def feasibility_ratios(self, rhs, rows, pivot_col):
        ratios = []
        for value, row in zip(rhs, rows):
            expanded_coef = -row[pivot_col]
            if expanded_coef <= 0:
                ratios.append(None)
            else:
                ratio = abs(value / expanded_coef)
                ratios.append(ratio if ratio > 0 else None)
        return ratios

    def optimization_ratios(self, rhs, rows, pivot_col):
        ratios = []
        for value, row in zip(rhs, rows):
            coef = row[pivot_col]
            if coef <= 0:
                ratios.append(None)
            else:
                ratios.append(value / coef)
        return ratios

    def choose_feasibility_pivot(self, basis, free, rhs, rows):
        negative_rows = [i for i, value in enumerate(rhs) if value < 0]
        if not negative_rows:
            return None

        target_row = min(negative_rows, key=lambda i: rhs[i])
        candidates = []
        current_negative_count = len(negative_rows)

        for col, row_coef in enumerate(rows[target_row]):
            if -row_coef <= 0:
                continue

            ratios = self.feasibility_ratios(rhs, rows, col)
            possible_rows = [
                i for i, row in enumerate(rows)
                if row[col] != 0
            ]
            if not possible_rows:
                continue

            for leaving_row in possible_rows:
                next_basis, next_free, next_rhs, next_rows = self.pivot(
                    basis, free, rhs, rows, leaving_row, col
                )
                negative_count = sum(1 for value in next_rhs if value < 0)
                target_fixed = (
                    target_row == leaving_row
                    or (target_row < len(next_rhs) and next_rhs[target_row] >= 0)
                )
                if negative_count > current_negative_count and not target_fixed:
                    continue
                ratio = ratios[leaving_row] if leaving_row < len(ratios) else None
                ratio_score = ratio if ratio is not None else Fraction(10**9)
                candidates.append((
                    negative_count,
                    not target_fixed,
                    leaving_row != target_row,
                    ratio_score,
                    col,
                    leaving_row,
                    ratios,
                ))

        if not candidates:
            return None

        _, _, _, _, col, row, ratios = min(candidates)
        return {
            "phase": "feasibility",
            "pivot_col": col,
            "pivot_row": row,
            "ratios": ratios,
            "target_row": target_row,
        }

    def choose_optimization_pivot(self, free, rhs, rows, objective_coeffs):
        candidates = [
            (coef, index)
            for index, coef in enumerate(objective_coeffs)
            if coef > 0
        ]
        if not candidates:
            return None

        _, pivot_col = max(candidates)
        ratios = self.optimization_ratios(rhs, rows, pivot_col)
        finite = [(value, i) for i, value in enumerate(ratios) if value is not None]
        if not finite:
            return {
                "phase": "optimization",
                "pivot_col": pivot_col,
                "pivot_row": None,
                "ratios": ratios,
            }

        _, pivot_row = min(finite)
        return {
            "phase": "optimization",
            "pivot_col": pivot_col,
            "pivot_row": pivot_row,
            "ratios": ratios,
        }

    def save_step(self, number, basis, free, rhs, rows, pivot=None):
        objective_constant, objective_coeffs = self.objective_expression(basis, free, rhs, rows)
        solution = self.basic_solution(basis, rhs)
        expressions = self.equations(basis, free, rhs, rows)

        description = ""
        if pivot is None:
            if any(value < 0 for value in rhs):
                description = "Базисное решение пока недопустимо: есть отрицательные компоненты."
            else:
                description = (
                    "В выражении целевой функции нет свободных переменных с положительными "
                    "коэффициентами. Критерий оптимальности выполнен."
                )
        elif pivot["phase"] == "feasibility":
            ratios = ", ".join(ratio_label(value) for value in pivot["ratios"])
            description = (
                "Базисное решение недопустимо, поэтому выбираем замену, уменьшающую число "
                f"отрицательных компонентов. В основные переменные переводим "
                f"{free[pivot['pivot_col']]}; min{{{ratios}}}."
            )
        else:
            ratios = ", ".join(ratio_label(value) for value in pivot["ratios"])
            description = (
                "Базисное решение допустимо. Для максимума выбираем свободную переменную "
                f"{free[pivot['pivot_col']]} с положительным коэффициентом в F; "
                f"min{{{ratios}}}."
            )

        self.steps.append({
            "title": f"Шаг {number}",
            "basis": basis[:],
            "free": free[:],
            "equations": expressions,
            "basic_solution": solution,
            "objective_expression": objective_text(objective_constant, objective_coeffs, free),
            "description": description,
            "pivot": None if pivot is None else {
                "phase": pivot["phase"],
                "entering": free[pivot["pivot_col"]],
                "leaving": basis[pivot["pivot_row"]] if pivot["pivot_row"] is not None else None,
                "pivot_row": pivot["pivot_row"],
                "pivot_col": pivot["pivot_col"],
                "ratios": [ratio_label(value) for value in pivot["ratios"]],
            },
        })

    def solve(self):
        basis, free, rhs, rows, canonical = self.build_initial()
        step_number = 1

        while step_number <= 50:
            if any(value < 0 for value in rhs):
                pivot = self.choose_feasibility_pivot(basis, free, rhs, rows)
            else:
                _, objective_coeffs = self.objective_expression(basis, free, rhs, rows)
                pivot = self.choose_optimization_pivot(free, rhs, rows, objective_coeffs)

            self.save_step(step_number, basis, free, rhs, rows, pivot)

            if pivot is None:
                if any(value < 0 for value in rhs):
                    status = "infeasible"
                    message = "Не удалось получить допустимое базисное решение."
                else:
                    status = "optimal"
                    message = "Оптимальное решение найдено."

                objective_constant, _ = self.objective_expression(basis, free, rhs, rows)
                if self.objective_type == "min":
                    objective_constant = -objective_constant

                return {
                    "status": status,
                    "message": message,
                    "canonical_system": canonical,
                    "steps": self.steps,
                    "solution": {
                        name: value
                        for name, value in self.basic_solution(basis, rhs).items()
                        if int(name.split("_")[1]) <= self.n
                    },
                    "objective_value": fmt(objective_constant) if status == "optimal" else None,
                }

            if pivot["pivot_row"] is None:
                return {
                    "status": "unbounded",
                    "message": "Целевая функция не ограничена на допустимой области.",
                    "canonical_system": canonical,
                    "steps": self.steps,
                    "solution": {},
                    "objective_value": None,
                }

            basis, free, rhs, rows = self.pivot(
                basis, free, rhs, rows, pivot["pivot_row"], pivot["pivot_col"]
            )
            step_number += 1

        raise ValueError("Превышено максимальное число шагов")
