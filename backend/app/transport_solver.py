from collections import deque
from fractions import Fraction

from app.simplex_solver import fr, fmt


def cell_name(i, j):
    return f"A_{i + 1}B_{j + 1}"


def matrix_fmt(matrix):
    return [[fmt(value) for value in row] for row in matrix]


def vector_fmt(values):
    return [fmt(value) for value in values]


def subtraction_fmt(left, right):
    return f"{fmt(left)}-({fmt(right)})" if right < 0 else f"{fmt(left)}-{fmt(right)}"


class TransportSolver:
    def __init__(self, costs, supply, demand):
        self.costs = [[fr(value) for value in row] for row in costs]
        self.supply = [fr(value) for value in supply]
        self.demand = [fr(value) for value in demand]
        self.steps = []
        self.balance_note = ""

    def balance(self):
        total_supply = sum(self.supply)
        total_demand = sum(self.demand)

        if total_supply == total_demand:
            self.balance_note = (
                f"Запасы поставщиков: {fmt(total_supply)}. "
                f"Потребность потребителей: {fmt(total_demand)}. "
                "Задача закрытая."
            )
            return

        if total_supply < total_demand:
            diff = total_demand - total_supply
            self.costs.append([Fraction(0) for _ in self.demand])
            self.supply.append(diff)
            self.balance_note = (
                f"Запасы поставщиков: {fmt(total_supply)}. "
                f"Потребность потребителей: {fmt(total_demand)}. "
                f"Разница {fmt(diff)}. Добавлен фиктивный поставщик с нулевыми тарифами."
            )
        else:
            diff = total_supply - total_demand
            for row in self.costs:
                row.append(Fraction(0))
            self.demand.append(diff)
            self.balance_note = (
                f"Запасы поставщиков: {fmt(total_supply)}. "
                f"Потребность потребителей: {fmt(total_demand)}. "
                f"Разница {fmt(diff)}. Добавлен фиктивный потребитель с нулевыми тарифами."
            )

    def empty_plan(self):
        return [[Fraction(0) for _ in self.demand] for _ in self.supply]

    def basis_cells(self, plan):
        return {
            (i, j)
            for i, row in enumerate(plan)
            for j, value in enumerate(row)
            if value > 0
        }

    def has_path(self, basis, start, finish):
        graph = {}
        for i, j in basis:
            row_node = ("r", i)
            col_node = ("c", j)
            graph.setdefault(row_node, set()).add(col_node)
            graph.setdefault(col_node, set()).add(row_node)

        start_node = ("r", start[0])
        finish_node = ("c", finish[1])
        queue = deque([start_node])
        seen = {start_node}

        while queue:
            node = queue.popleft()
            if node == finish_node:
                return True
            for nxt in graph.get(node, set()):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return False

    def complete_basis(self, basis):
        required = len(self.supply) + len(self.demand) - 1
        added = []

        for i in range(len(self.supply)):
            for j in range(len(self.demand)):
                if len(basis) >= required:
                    return added
                if (i, j) in basis:
                    continue
                if not self.has_path(basis, (i, j), (i, j)):
                    basis.add((i, j))
                    added.append(cell_name(i, j))

        return added

    def initial_plan(self):
        supply_left = self.supply[:]
        demand_left = self.demand[:]
        active_rows = set(range(len(supply_left)))
        active_cols = set(range(len(demand_left)))
        plan = self.empty_plan()
        allocations = []

        while active_rows and active_cols:
            candidates = []
            for i in active_rows:
                for j in active_cols:
                    dummy_penalty = 1 if self.supply[i] != 0 and self.costs[i][j] == 0 else 0
                    is_dummy_row = i == len(self.supply) - 1 and all(c == 0 for c in self.costs[i])
                    is_dummy_col = j == len(self.demand) - 1 and all(row[j] == 0 for row in self.costs)
                    dummy_penalty = 1 if is_dummy_row or is_dummy_col else dummy_penalty
                    candidates.append((dummy_penalty, self.costs[i][j], i, j))

            _, _, i, j = min(candidates)
            amount = min(supply_left[i], demand_left[j])
            supply_before = supply_left[i]
            demand_before = demand_left[j]
            plan[i][j] = amount
            supply_left[i] -= amount
            demand_left[j] -= amount
            allocations.append({
                "cell": cell_name(i, j),
                "row": i,
                "col": j,
                "amount": fmt(amount),
                "calculation": f"{fmt(amount)}=min{{{fmt(supply_before)},{fmt(demand_before)}}}",
                "supply_before": fmt(supply_before),
                "supply_after": fmt(supply_left[i]),
                "demand_before": fmt(demand_before),
                "demand_after": fmt(demand_left[j]),
            })

            if supply_left[i] == 0 and demand_left[j] == 0:
                active_rows.remove(i)
            elif supply_left[i] == 0:
                active_rows.remove(i)
            elif demand_left[j] == 0:
                active_cols.remove(j)

        return plan, allocations

    def cost_total(self, plan):
        total = Fraction(0)
        terms = []
        for i, row in enumerate(plan):
            for j, amount in enumerate(row):
                if amount > 0:
                    total += amount * self.costs[i][j]
                    terms.append(f"{fmt(amount)}∙{fmt(self.costs[i][j])}")
        return total, "+".join(terms) + f"={fmt(total)}"

    def potentials(self, basis):
        m = len(self.supply)
        n = len(self.demand)
        u = [None for _ in range(m)]
        v = [None for _ in range(n)]
        calculations = ["Пусть u_1=0."]
        u[0] = Fraction(0)
        changed = True

        while changed:
            changed = False
            for i, j in sorted(basis):
                if u[i] is not None and v[j] is None:
                    v[j] = self.costs[i][j] - u[i]
                    calculations.append(
                        f"{cell_name(i, j)}: u_{i + 1}+v_{j + 1}={fmt(self.costs[i][j])}; "
                        f"v_{j + 1}={subtraction_fmt(self.costs[i][j], u[i])}={fmt(v[j])}"
                    )
                    changed = True
                elif v[j] is not None and u[i] is None:
                    u[i] = self.costs[i][j] - v[j]
                    calculations.append(
                        f"{cell_name(i, j)}: u_{i + 1}+v_{j + 1}={fmt(self.costs[i][j])}; "
                        f"u_{i + 1}={subtraction_fmt(self.costs[i][j], v[j])}={fmt(u[i])}"
                    )
                    changed = True

        for i, value in enumerate(u):
            if value is None:
                u[i] = Fraction(0)
        for j, value in enumerate(v):
            if value is None:
                v[j] = Fraction(0)

        return u, v, calculations

    def estimates(self, basis, u, v):
        values = []
        for i in range(len(self.supply)):
            for j in range(len(self.demand)):
                if (i, j) in basis:
                    continue
                delta = self.costs[i][j] - (u[i] + v[j])
                values.append({
                    "cell": cell_name(i, j),
                    "i": i,
                    "j": j,
                    "value": delta,
                    "text": (
                        f"Δ_{i + 1}{j + 1}="
                        f"{fmt(self.costs[i][j])}-({fmt(u[i])}+{fmt(v[j])})={fmt(delta)}"
                    ),
                })
        return values

    def find_cycle(self, basis, entering):
        cells = list(basis | {entering})
        rows = {}
        cols = {}
        for cell in cells:
            rows.setdefault(cell[0], []).append(cell)
            cols.setdefault(cell[1], []).append(cell)

        def neighbors(cell):
            for other in rows[cell[0]]:
                if other != cell:
                    yield other
            for other in cols[cell[1]]:
                if other != cell:
                    yield other

        start = entering
        queue = deque([(start, [start])])
        while queue:
            cell, path = queue.popleft()
            for nxt in neighbors(cell):
                if nxt == start and len(path) >= 4:
                    return path
                if nxt in path:
                    continue
                if len(path) >= 2:
                    prev = path[-2]
                    same_row_prev = prev[0] == cell[0]
                    same_row_next = nxt[0] == cell[0]
                    if same_row_prev == same_row_next:
                        continue
                queue.append((nxt, path + [nxt]))
        return None

    def improve_plan(self, plan, basis, entering):
        cycle = self.find_cycle(basis, entering)
        if not cycle:
            raise ValueError("Не удалось построить цикл перераспределения")

        minus_cells = cycle[1::2]
        theta = min(plan[i][j] for i, j in minus_cells)

        for index, (i, j) in enumerate(cycle):
            if index % 2 == 0:
                plan[i][j] += theta
            else:
                plan[i][j] -= theta

        leaving_candidates = [(i, j) for i, j in minus_cells if plan[i][j] == 0]
        leaving = leaving_candidates[0]
        basis.add(entering)
        basis.remove(leaving)

        return {
            "cycle": [
                {
                    "cell": cell_name(i, j),
                    "sign": "+" if index % 2 == 0 else "-",
                }
                for index, (i, j) in enumerate(cycle)
            ],
            "theta": fmt(theta),
            "leaving": cell_name(*leaving),
        }

    def save_step(
        self,
        title,
        plan,
        basis,
        u=None,
        v=None,
        estimates=None,
        note="",
        cycle=None,
        potential_calculations=None,
    ):
        total, formula = self.cost_total(plan)
        if potential_calculations is None and u is not None and v is not None:
            potential_calculations = self.potentials(basis)[2]
        self.steps.append({
            "title": title,
            "note": note,
            "plan": matrix_fmt(plan),
            "costs": matrix_fmt(self.costs),
            "supply": vector_fmt(self.supply),
            "demand": vector_fmt(self.demand),
            "basis": [cell_name(i, j) for i, j in sorted(basis)],
            "u": [] if u is None else vector_fmt(u),
            "v": [] if v is None else vector_fmt(v),
            "potential_calculations": [] if potential_calculations is None else potential_calculations,
            "estimates": [] if estimates is None else [
                {
                    "cell": item["cell"],
                    "value": fmt(item["value"]),
                    "text": item["text"],
                }
                for item in estimates
            ],
            "cycle": cycle,
            "total_cost": fmt(total),
            "cost_formula": formula,
        })

    def solve(self):
        self.balance()
        plan, allocations = self.initial_plan()
        basis = self.basis_cells(plan)
        required_basis = len(self.supply) + len(self.demand) - 1
        artificial_basis = self.complete_basis(basis)

        self.save_step(
            "Начальный опорный план",
            plan,
            basis,
            note=(
                self.balance_note
                + f" Количество задействованных маршрутов: {len(basis)}; "
                + f"необходимо {required_basis}. "
                + "Начальный план построен методом минимального тарифа."
                + (
                    f" Для устранения вырожденности в базис добавлены нулевые клетки: "
                    f"{', '.join(artificial_basis)}."
                    if artificial_basis
                    else ""
                )
            ),
        )
        self.steps[-1]["allocations"] = allocations

        iteration = 1
        while iteration <= 20:
            u, v, potential_calculations = self.potentials(basis)
            deltas = self.estimates(basis, u, v)
            negative = [item for item in deltas if item["value"] < 0]

            if not negative:
                self.save_step(
                    "Проверка оптимальности",
                    plan,
                    basis,
                    u,
                    v,
                    deltas,
                    "Все оценки свободных клеток неотрицательны. План оптимален.",
                )
                total, _ = self.cost_total(plan)
                return {
                    "status": "optimal",
                    "message": "Оптимальный план найден.",
                    "balanced": {
                        "costs": matrix_fmt(self.costs),
                        "supply": vector_fmt(self.supply),
                        "demand": vector_fmt(self.demand),
                        "note": self.balance_note,
                    },
                    "steps": self.steps,
                    "solution": matrix_fmt(plan),
                    "total_cost": fmt(total),
                }

            entering = min(negative, key=lambda item: item["value"])
            cycle = self.improve_plan(plan, basis, (entering["i"], entering["j"]))
            self.save_step(
                f"Улучшение плана {iteration}",
                plan,
                basis,
                u,
                v,
                deltas,
                f"Есть отрицательная оценка {entering['cell']}: {fmt(entering['value'])}. "
                "Перераспределяем поставки по циклу.",
                cycle,
                potential_calculations,
            )
            iteration += 1

        raise ValueError("Превышено максимальное число итераций")
