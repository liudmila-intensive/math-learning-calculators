from math import prod

from sympy import Eq, Poly, S, discriminant, expand, factor, fraction, latex, simplify, solveset, together

from app.algebra import find_matching_parenthesis, parse_math_expression


def split_equation(equation: str):
    if "=" not in equation:
        return equation, "0"

    left, right = equation.split("=", 1)
    return left.strip(), right.strip()


def parse_log_side(text: str):
    prepared = text.strip().replace(" ", "")
    log_index = prepared.find("log_")
    if log_index == -1:
        return None

    coefficient_text = prepared[:log_index]
    if coefficient_text.endswith("*"):
        coefficient_text = coefficient_text[:-1]
    coefficient = parse_math_expression(coefficient_text) if coefficient_text else S.One

    log_text = prepared[log_index:]
    if not log_text.startswith("log_"):
        return None

    argument_start = log_text.find("(", 4)
    if argument_start == -1:
        return None

    argument_end = find_matching_parenthesis(log_text, argument_start)
    if argument_end != len(log_text) - 1:
        return None

    base_text = log_text[4:argument_start]
    argument_text = log_text[argument_start + 1:argument_end]
    if not base_text or not argument_text:
        return None

    return {
        "coefficient_text": coefficient_text or "1",
        "coefficient": coefficient,
        "base_text": base_text,
        "argument_text": argument_text,
        "base": parse_math_expression(base_text),
        "argument": parse_math_expression(argument_text),
        "powered_argument": parse_math_expression(argument_text) ** coefficient,
    }


def strip_outer_parentheses(text: str):
    prepared = text.strip()
    if prepared.startswith("(") and find_matching_parenthesis(prepared, 0) == len(prepared) - 1:
        return prepared[1:-1]
    return prepared


def split_top_level(text: str, separator: str):
    parts = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == separator and depth == 0:
            parts.append(text[start:index])
            start = index + 1
    parts.append(text[start:])
    return parts


def parse_power_term(text: str):
    parts = split_top_level(text, "^")
    if len(parts) != 2:
        return None
    try:
        base = int(strip_outer_parentheses(parts[0]))
    except ValueError:
        return None
    exponent_text = strip_outer_parentheses(parts[1])
    return {"base": base, "exponent_text": exponent_text, "exponent": parse_math_expression(exponent_text)}


def parse_power_product_side(text: str):
    prepared = text.strip().replace(" ", "")
    factors = [parse_power_term(part) for part in split_top_level(prepared, "*")]
    if not factors or any(factor is None for factor in factors):
        return None
    exponent_text = factors[0]["exponent_text"]
    if any(factor["exponent_text"] != exponent_text for factor in factors):
        return None
    return {
        "bases": [factor["base"] for factor in factors],
        "base_product": S.One * int(prod(factor["base"] for factor in factors)),
        "exponent_text": exponent_text,
        "exponent": factors[0]["exponent"],
    }


def parse_single_power_side(text: str):
    return parse_power_term(text.strip().replace(" ", ""))


def integer_power(base, target):
    current = base
    for power in range(1, 12):
        if current == target:
            return power
        current *= base
    return None


def parse_exponential_equation(left_text: str, right_text: str):
    left_product = parse_power_product_side(left_text)
    right_power = parse_single_power_side(right_text)
    if not left_product or not right_power:
        return None

    common_base = left_product["base_product"]
    right_power_multiplier = integer_power(int(common_base), right_power["base"])
    if right_power_multiplier is None:
        return None

    return {
        "left": left_product,
        "right": right_power,
        "common_base": common_base,
        "right_power_multiplier": S(right_power_multiplier),
    }


def is_square_root(expr):
    return expr.is_Pow and expr.exp == S.Half


def detect_variable(expr, requested_variable=None):
    if requested_variable:
        variable = parse_math_expression(requested_variable)
        if not variable.is_Symbol:
            raise ValueError("Переменная должна быть обозначена одной буквой, например x.")
        return variable

    symbols = sorted(expr.free_symbols, key=lambda item: item.name)
    if not symbols:
        raise ValueError("В уравнении нет переменной.")
    if len(symbols) > 1:
        raise ValueError(
            "В уравнении несколько переменных. Укажите, относительно какой переменной решать."
        )
    return symbols[0]


def solution_latex(variable, solutions):
    if not solutions:
        return "\\varnothing"
    if len(solutions) == 1:
        return f"{latex(variable)} = {latex(solutions[0])}"
    return ";\\ ".join(f"{latex(variable)}_{{{index + 1}}} = {latex(value)}" for index, value in enumerate(solutions))


def section_step(title):
    return {
        "expression": title,
        "explanation": "",
        "latex": "",
        "is_section": True,
    }


def coefficient_term_latex(coef, variable):
    if coef == 1:
        return latex(variable)
    if coef == -1:
        return f"-{latex(variable)}"
    return latex(coef * variable)


def negated_latex(value):
    if value < 0:
        return f"-({latex(value)})"
    return f"-{latex(value)}"


def squared_substitution_latex(value):
    if value < 0:
        return f"\\left({latex(value)}\\right)^2"
    return f"{latex(value)}^2"


def sorted_real_solutions(solution_set):
    return sorted(list(solution_set), key=lambda item: float(item.evalf()))


def domain_latex(variable_expr, excluded_values):
    if not excluded_values:
        return f"{latex(variable_expr)} \\in \\mathbb{{R}}"
    return ",\\ ".join(f"{latex(variable_expr)} \\ne {latex(value)}" for value in excluded_values)


def build_rational_equation_result(left, right, left_text, right_text, variable_expr):
    rational_expr = together(left - right)
    numerator, denominator = fraction(rational_expr)
    numerator = expand(numerator)
    denominator = factor(denominator)
    excluded_values = sorted_real_solutions(solveset(Eq(denominator, 0), variable_expr, domain=S.Reals))
    candidate_solutions = sorted_real_solutions(solveset(Eq(numerator, 0), variable_expr, domain=S.Reals))
    solutions = [value for value in candidate_solutions if value not in excluded_values]
    result_latex = solution_latex(variable_expr, solutions)

    if not solutions:
        result_text = "нет действительных корней"
    elif len(solutions) == 1:
        result_text = f"{variable_expr} = {solutions[0]}"
    else:
        result_text = "; ".join(
            f"{variable_expr}_{index + 1} = {value}"
            for index, value in enumerate(solutions)
        )

    domain_check = (
        f"{latex(denominator)} \\ne 0 \\Longleftrightarrow {domain_latex(variable_expr, excluded_values)}"
        if excluded_values
        else f"{latex(denominator)} \\ne 0"
    )
    multiplied_left = simplify(left * denominator)
    multiplied_right = simplify(right * denominator)
    multiplied_latex = f"{latex(multiplied_left)} = {latex(multiplied_right)}"
    expanded_latex = f"{latex(expand(multiplied_left))} = {latex(expand(multiplied_right))}"
    numerator_latex = f"{latex(numerator)} = 0"
    factored = factor(numerator)

    steps = [
        {
            "expression": f"{left_text}={right_text}",
            "explanation": "Записываем исходное уравнение и находим ОДЗ",
            "latex": (
                "\\begin{aligned}"
                f"{latex(simplify(left))}&={latex(simplify(right))}\\\\"
                f"{domain_check}"
                "\\end{aligned}"
            ),
            "is_chain": True,
        },
        {
            "expression": str(numerator),
            "explanation": "Умножаем обе части уравнения на общий знаменатель",
            "latex": (
                f"{latex(simplify(left))} = {latex(simplify(right))} "
                f"\\Longleftrightarrow {multiplied_latex}"
                + (f" \\Longleftrightarrow {expanded_latex}" if expanded_latex != multiplied_latex else "")
            ),
            "is_chain": True,
        },
        {
            "expression": str(factored),
            "explanation": "Переносим все слагаемые в левую часть и решаем полученное уравнение",
            "latex": (
                f"{numerator_latex}"
                + (f" \\Longleftrightarrow {latex(factored)} = 0" if factored != numerator else "")
                + f" \\Longleftrightarrow {solution_latex(variable_expr, candidate_solutions)}"
            ),
            "is_chain": True,
        },
    ]

    if excluded_values:
        steps.append({
            "expression": str(solutions),
            "explanation": "Проверяем корни по ОДЗ и исключаем запрещенные значения",
            "latex": f"{domain_latex(variable_expr, excluded_values)} \\Longrightarrow {result_latex}",
            "is_chain": True,
        })

    return result_text, result_latex, steps, solutions, numerator


def build_logarithmic_equation_result(log_left, log_right, left_text, right_text, variable_expr):
    left_argument = log_left["argument"]
    right_argument = log_right["argument"]
    left_powered = expand(log_left["powered_argument"])
    right_powered = expand(log_right["powered_argument"])
    base = log_left["base"]
    base_latex = latex(base)
    candidate_solutions = sorted_real_solutions(
        solveset(Eq(left_powered, right_powered), variable_expr, domain=S.Reals)
    )
    solutions = [
        value for value in candidate_solutions
        if left_argument.subs(variable_expr, value).evalf() > 0
        and right_argument.subs(variable_expr, value).evalf() > 0
    ]
    result_latex = solution_latex(variable_expr, solutions)

    if not solutions:
        result_text = "нет действительных корней"
    elif len(solutions) == 1:
        result_text = f"{variable_expr} = {solutions[0]}"
    else:
        result_text = "; ".join(
            f"{variable_expr}_{index + 1} = {value}"
            for index, value in enumerate(solutions)
        )

    domain_latex_text = (
        f"{base_latex}>0,\\ {base_latex}\\ne 1,\\ "
        f"{latex(left_argument)}>0,\\ {latex(right_argument)}>0"
    )
    equal_arguments_latex = f"{latex(left_powered)} = {latex(right_powered)}"
    _, _, linear_steps = build_linear_equation_result(
        left_powered,
        right_powered,
        log_left["argument_text"],
        log_right["argument_text"],
        variable_expr,
        candidate_solutions,
    )

    steps = [
        {
            "expression": f"{left_text}={right_text}",
            "explanation": "Записываем логарифмическое уравнение и ОДЗ: основание положительно и не равно 1, выражения под логарифмами положительны",
            "latex": (
                "\\begin{aligned}"
                f"{log_side_latex(log_left)}&={log_side_latex(log_right)}\\\\"
                f"{domain_latex_text}"
                "\\end{aligned}"
            ),
            "is_chain": True,
        },
    ]

    property_parts = []
    if log_left["coefficient"] != 1:
        property_parts.append(
            f"{latex(log_left['coefficient'])}\\log_{{{base_latex}}}\\left({latex(left_argument)}\\right)"
            f"=\\log_{{{base_latex}}}\\left({latex(left_argument)}^{{{latex(log_left['coefficient'])}}}\\right)"
            f"=\\log_{{{base_latex}}}\\left({latex(left_powered)}\\right)"
        )
    if log_right["coefficient"] != 1:
        property_parts.append(
            f"{latex(log_right['coefficient'])}\\log_{{{base_latex}}}\\left({latex(right_argument)}\\right)"
            f"=\\log_{{{base_latex}}}\\left({latex(right_argument)}^{{{latex(log_right['coefficient'])}}}\\right)"
            f"=\\log_{{{base_latex}}}\\left({latex(right_powered)}\\right)"
        )

    if property_parts:
        steps.append({
            "expression": " ".join(property_parts),
            "explanation": "Используем свойство: множитель перед логарифмом переносим в степень подлогарифмического выражения",
            "latex": " \\quad ".join(property_parts),
            "is_chain": True,
        })

    steps.extend([
        {
            "expression": f"{log_left['argument_text']}={log_right['argument_text']}",
            "explanation": "Так как основания логарифмов одинаковые, приравниваем выражения под логарифмами",
            "latex": (
                f"\\log_{{{base_latex}}}\\left({latex(left_powered)}\\right)"
                f"=\\log_{{{base_latex}}}\\left({latex(right_powered)}\\right)"
                f" \\Longleftrightarrow {equal_arguments_latex}"
            ),
            "is_chain": True,
        },
    ])

    if linear_steps:
        linear_step = linear_steps[0].copy()
        linear_step["explanation"] = "Решаем полученное уравнение"
        steps.append(linear_step)

    steps.append({
        "expression": str(solutions),
        "explanation": "Проверяем найденные корни по ОДЗ",
        "latex": f"{domain_latex_text} \\Longrightarrow {result_latex}",
        "is_chain": True,
    })

    return result_text, result_latex, steps, solutions, expand(left_powered - right_powered)


def log_side_latex(log_data):
    base_latex = latex(log_data["base"])
    argument_latex = latex(log_data["argument"])
    log_latex = f"\\log_{{{base_latex}}}\\left({argument_latex}\\right)"
    if log_data["coefficient"] == 1:
        return log_latex
    return f"{latex(log_data['coefficient'])}{log_latex}"


def power_term_latex(base, exponent):
    return f"{latex(base)}^{{{latex(exponent)}}}"


def build_exponential_equation_result(data, left_text, right_text):
    left_data = data["left"]
    right_data = data["right"]
    common_base = data["common_base"]
    right_multiplier = data["right_power_multiplier"]
    variable_expr = detect_variable(left_data["exponent"] + right_data["exponent"])

    left_exponent = left_data["exponent"]
    right_exponent = expand(right_multiplier * right_data["exponent"])
    candidate_solutions = sorted_real_solutions(solveset(Eq(left_exponent, right_exponent), variable_expr, domain=S.Reals))
    result_latex = solution_latex(variable_expr, candidate_solutions)
    result_text = (
        "нет действительных корней"
        if not candidate_solutions
        else "; ".join(f"{variable_expr}_{index + 1} = {value}" for index, value in enumerate(candidate_solutions))
        if len(candidate_solutions) > 1
        else f"{variable_expr} = {candidate_solutions[0]}"
    )

    original_left_latex = "\\cdot ".join(
        power_term_latex(base, left_exponent) for base in left_data["bases"]
    )
    original_right_latex = power_term_latex(right_data["base"], right_data["exponent"])
    product_base_latex = "\\cdot ".join(latex(base) for base in left_data["bases"])
    combined_left_latex = f"\\left({product_base_latex}\\right)^{{{latex(left_exponent)}}}"
    common_left_latex = power_term_latex(common_base, left_exponent)
    right_base_power_latex = f"\\left({power_term_latex(common_base, right_multiplier)}\\right)^{{{latex(right_data['exponent'])}}}"
    common_right_latex = power_term_latex(common_base, right_exponent)

    _, _, linear_steps = build_linear_equation_result(
        left_exponent,
        right_exponent,
        left_data["exponent_text"],
        str(right_exponent),
        variable_expr,
        candidate_solutions,
    )

    steps = [
        {
            "expression": f"{left_text}={right_text}",
            "explanation": "Записываем исходное степенное уравнение",
            "latex": f"{original_left_latex}={original_right_latex}",
            "is_chain": True,
        },
        {
            "expression": str(common_base),
            "explanation": "Используем свойство: произведение степеней с одинаковыми показателями равно степени произведения оснований",
            "latex": (
                f"{original_left_latex}={original_right_latex}"
                f" \\Longleftrightarrow {combined_left_latex}={original_right_latex}"
                f" \\Longleftrightarrow {common_left_latex}={original_right_latex}"
            ),
            "is_chain": True,
        },
        {
            "expression": str(right_exponent),
            "explanation": "Представляем правую часть через то же основание и используем свойство степени степени",
            "latex": (
                f"{common_left_latex}={original_right_latex}"
                f" \\Longleftrightarrow {common_left_latex}={right_base_power_latex}"
                f" \\Longleftrightarrow {common_left_latex}={common_right_latex}"
            ),
            "is_chain": True,
        },
        {
            "expression": f"{left_exponent}={right_exponent}",
            "explanation": "Так как основания одинаковые и положительные, приравниваем показатели",
            "latex": f"{common_left_latex}={common_right_latex} \\Longleftrightarrow {latex(left_exponent)}={latex(right_exponent)}",
            "is_chain": True,
        },
    ]

    if linear_steps:
        linear_step = linear_steps[0].copy()
        linear_step["explanation"] = "Решаем полученное линейное уравнение"
        steps.append(linear_step)

    return result_text, result_latex, steps, candidate_solutions, expand(left_exponent - right_exponent)


def build_radical_equation_result(left, right, left_text, right_text):
    if is_square_root(left):
        radical_side = left
        other_side = right
    elif is_square_root(right):
        radical_side = right
        other_side = left
    else:
        return None

    radicand = radical_side.base
    variable_expr = detect_variable(radicand + other_side)
    squared_left = expand(radicand)
    squared_right = expand(other_side ** 2)
    normalized = expand(squared_left - squared_right)
    candidate_solutions = sorted_real_solutions(solveset(Eq(normalized, 0), variable_expr, domain=S.Reals))
    solutions = [
        value for value in candidate_solutions
        if radicand.subs(variable_expr, value).evalf() >= 0
        and other_side.subs(variable_expr, value).evalf() >= 0
        and simplify(radical_side.subs(variable_expr, value) - other_side.subs(variable_expr, value)) == 0
    ]
    result_latex = solution_latex(variable_expr, solutions)
    result_text = (
        "нет действительных корней"
        if not solutions
        else f"{variable_expr} = {solutions[0]}"
        if len(solutions) == 1
        else "; ".join(f"{variable_expr}_{index + 1} = {value}" for index, value in enumerate(solutions))
    )

    _, _, quadratic_steps = build_quadratic_equation_result(
        squared_left,
        squared_right,
        str(squared_left),
        str(squared_right),
        variable_expr,
        normalized,
        candidate_solutions,
    )

    steps = [
        {
            "expression": f"{left_text}={right_text}",
            "explanation": "Записываем исходное иррациональное уравнение и ОДЗ",
            "latex": (
                "\\begin{aligned}"
                f"{latex(left)}&={latex(right)}\\\\"
                f"{latex(radicand)}&\\ge 0,\\quad {latex(other_side)}\\ge 0"
                "\\end{aligned}"
            ),
            "is_chain": True,
        },
        {
            "expression": str(normalized),
            "explanation": "Возводим обе части уравнения в квадрат",
            "latex": (
                f"{latex(left)}={latex(right)}"
                f" \\Longleftrightarrow {latex(squared_left)}={latex(squared_right)}"
            ),
            "is_chain": True,
        },
        {
            "expression": str(normalized),
            "explanation": "Раскрываем скобки и переносим все слагаемые в левую часть",
            "latex": (
                f"{latex(squared_left)}={latex(squared_right)}"
                f" \\Longleftrightarrow {latex(normalized)}=0"
            ),
            "is_chain": True,
        },
    ]

    steps.extend(quadratic_steps[1:])
    steps.append({
        "expression": str(solutions),
        "explanation": "Проверяем найденные корни в исходном уравнении и оставляем подходящие",
        "latex": f"{latex(left)}={latex(right)} \\Longrightarrow {result_latex}",
        "is_chain": True,
    })

    return result_text, result_latex, steps, solutions, normalized


def build_linear_equation_result(left, right, left_text, right_text, variable_expr, solutions):
    expanded_left = expand(left)
    expanded_right = expand(right)
    left_poly = Poly(expand(left), variable_expr)
    right_poly = Poly(expand(right), variable_expr)
    left_coeff = left_poly.coeff_monomial(variable_expr)
    right_coeff = right_poly.coeff_monomial(variable_expr)
    left_free = left_poly.coeff_monomial(1)
    right_free = right_poly.coeff_monomial(1)
    total_coeff = left_coeff - right_coeff
    free_shift = right_free - left_free

    result_latex = solution_latex(variable_expr, solutions)
    if total_coeff == 0:
        if free_shift == 0:
            result_text = "любое действительное число"
            result_latex = f"{latex(variable_expr)} \\in \\mathbb{{R}}"
        else:
            result_text = "нет действительных корней"
            result_latex = "\\varnothing"
        return result_text, result_latex, [{
            "expression": f"{left_text}={right_text}",
            "explanation": "Проверяем линейное уравнение",
            "latex": f"{latex(left)} = {latex(right)} \\Longleftrightarrow {latex(total_coeff)} = {latex(free_shift)} \\Longleftrightarrow {result_latex}",
            "is_chain": True,
        }]

    variable_part = coefficient_term_latex(total_coeff, variable_expr)
    shifted_expr = right_free - left_free
    solution = solutions[0] if solutions else free_shift / total_coeff

    if left_free == 0:
        first_isolation = f"{variable_part} = {latex(right_free)}"
    else:
        first_isolation = (
            f"{variable_part} = {latex(right_free)}"
            f"{'-' if left_free >= 0 else '+'}{latex(abs(left_free))}"
        )

    divided_latex = (
        f"{latex(variable_expr)} = {latex(shifted_expr)}"
        f"\\colon {latex(total_coeff)}"
    )
    chain_parts = [f"{latex(left)} = {latex(right)}"]
    has_expansion_step = latex(expanded_left) != latex(left) or latex(expanded_right) != latex(right)
    if has_expansion_step:
        chain_parts.append(f"{latex(expanded_left)} = {latex(expanded_right)}")

    chain_parts.append(first_isolation)

    simplified_isolation = f"{variable_part} = {latex(free_shift)}"
    if simplified_isolation != first_isolation:
        chain_parts.append(simplified_isolation)

    chain_parts.extend([divided_latex, result_latex])
    chain_latex = " \\Longleftrightarrow ".join(chain_parts)

    explanation = (
        "Раскрываем скобки, переносим свободные слагаемые, выполняем вычисления и делим обе части на коэффициент при переменной"
        if has_expansion_step
        else "Переносим свободные слагаемые, выполняем вычисления и делим обе части на коэффициент при переменной"
    )

    steps = [{
        "expression": " <=> ".join(chain_parts),
        "explanation": explanation,
        "latex": chain_latex,
        "is_chain": True,
    }]

    return f"{variable_expr} = {solution}", result_latex, steps


def is_vieta_friendly(a, roots):
    return a == 1 and len(roots) == 2 and all(root.is_Rational for root in roots)


def build_quadratic_equation_result(left, right, left_text, right_text, variable_expr, normalized, solutions):
    poly = Poly(normalized, variable_expr)
    a = poly.coeff_monomial(variable_expr ** 2)
    b = poly.coeff_monomial(variable_expr)
    c = poly.coeff_monomial(1)
    result_latex = solution_latex(variable_expr, solutions)
    result_text = (
        "нет действительных корней"
        if not solutions
        else "; ".join(f"{variable_expr}_{index + 1} = {value}" for index, value in enumerate(solutions))
    )
    original_latex = f"{latex(simplify(left))} = {latex(simplify(right))}"
    normalized_latex = f"{latex(normalized)} = 0"
    initial_latex = (
        original_latex
        if simplify(left - normalized) == 0 and right == 0
        else f"{original_latex} \\Longleftrightarrow {normalized_latex}"
    )

    steps = [{
        "expression": f"{left_text}={right_text}",
        "explanation": "Записываем исходное уравнение и приводим его к виду ax²+bx+c=0",
        "latex": initial_latex,
        "is_chain": True,
    }]

    factored = factor(normalized)
    is_incomplete = b == 0 or c == 0
    if is_incomplete:
        if c == 0:
            steps.append(section_step("I. Разложение на множители"))
            factored_latex = latex(factored)
            steps.append({
                "expression": str(factored),
                "explanation": "Выносим общий множитель за скобки и приравниваем каждый множитель к нулю",
                "latex": f"{latex(normalized)} = 0 \\Longleftrightarrow {factored_latex} = 0 \\Longleftrightarrow {result_latex}",
                "is_chain": True,
            })
        elif b == 0 and factored.is_Mul:
            steps.append(section_step("I. Разложение на множители"))
            steps.append({
                "expression": str(factored),
                "explanation": "Раскладываем левую часть по формуле разности квадратов",
                "latex": f"{latex(normalized)} = 0 \\Longleftrightarrow {latex(factored)} = 0 \\Longleftrightarrow {result_latex}",
                "is_chain": True,
            })
        else:
            steps.append(section_step("I. Неполное квадратное уравнение"))
            shifted = -c / a
            steps.append({
                "expression": str(shifted),
                "explanation": "Выражаем квадрат переменной и извлекаем корень",
                "latex": (
                    f"{latex(a * variable_expr ** 2)} = {latex(-c)} "
                    f"\\Longleftrightarrow {latex(variable_expr ** 2)} = {latex(shifted)} "
                    f"\\Longleftrightarrow {result_latex}"
                ),
                "is_chain": True,
            })

        return result_text, result_latex, steps

    if is_vieta_friendly(a, solutions):
        steps.append(section_step("I. Теорема Виета"))
        p = b
        q = c
        sum_roots = -p
        product_roots = q
        steps.append({
            "expression": str(solutions),
            "explanation": "Подбираем числа, сумма которых равна -p, а произведение равно q",
            "latex": (
                f"{latex(variable_expr)}_1+{latex(variable_expr)}_2={latex(sum_roots)},\\quad "
                f"{latex(variable_expr)}_1\\cdot {latex(variable_expr)}_2={latex(product_roots)} "
                f"\\Longleftrightarrow {result_latex}"
            ),
            "is_chain": True,
        })
        steps.append(section_step("II. Дискриминант"))
    else:
        steps.append(section_step("I. Дискриминант"))

    d = discriminant(normalized, variable_expr)
    d_latex = (
        f"D&=b^2-4ac={squared_substitution_latex(b)}"
        f"-4\\cdot {latex(a)}\\cdot {latex(c)}={latex(d)}"
    )
    if d < 0:
        discriminant_latex = (
            "\\begin{aligned}"
            f"{d_latex}\\\\D&<0,\\ \\text{{действительных корней нет}}"
            "\\end{aligned}"
        )
    elif d == 0:
        discriminant_latex = (
            "\\begin{aligned}"
            f"{d_latex}\\\\{latex(variable_expr)}&=\\frac{{{negated_latex(b)}}}{{2\\cdot {latex(a)}}}={latex(solutions[0])}"
            "\\end{aligned}"
        )
    else:
        denominator = f"2\\cdot {latex(a)}"
        x1 = solutions[0]
        x2 = solutions[1]
        discriminant_latex = (
            "\\begin{aligned}"
            f"{d_latex}\\\\"
            f"{latex(variable_expr)}_1&=\\frac{{-b-\\sqrt{{D}}}}{{2a}},\\quad "
            f"{latex(variable_expr)}_2=\\frac{{-b+\\sqrt{{D}}}}{{2a}}\\\\"
            f"{latex(variable_expr)}_1&=\\frac{{{negated_latex(b)}-\\sqrt{{{latex(d)}}}}}{{{denominator}}}={latex(x1)}\\\\"
            f"{latex(variable_expr)}_2&=\\frac{{{negated_latex(b)}+\\sqrt{{{latex(d)}}}}}{{{denominator}}}={latex(x2)}"
            "\\end{aligned}"
        )

    steps.append({
        "expression": str(d),
        "explanation": "Находим дискриминант и корни по формуле",
        "latex": discriminant_latex,
        "is_chain": True,
    })

    return result_text, result_latex, steps


def build_equation_steps(equation: str, variable: str | None = None):
    left_text, right_text = split_equation(equation)
    exponential_data = parse_exponential_equation(left_text, right_text)
    if exponential_data:
        result_text, result_latex, steps, solutions, normalized = build_exponential_equation_result(
            exponential_data,
            left_text,
            right_text,
        )
        variable_expr = detect_variable(normalized)
        return {
            "original": f"{left_text}={right_text}",
            "variable": str(variable_expr),
            "normalized": str(normalized),
            "result": result_text,
            "result_latex": result_latex,
            "chain_latex": " \\Longleftrightarrow ".join(step["latex"] for step in steps if step.get("latex")),
            "steps": steps,
            "solutions": [str(item) for item in solutions],
        }

    log_left = parse_log_side(left_text)
    log_right = parse_log_side(right_text)
    if log_left and log_right and simplify(log_left["base"] - log_right["base"]) == 0:
        variable_expr = detect_variable(log_left["argument"] - log_right["argument"], variable)
        result_text, result_latex, steps, solutions, normalized = build_logarithmic_equation_result(
            log_left,
            log_right,
            left_text,
            right_text,
            variable_expr,
        )
        return {
            "original": f"{left_text}={right_text}",
            "variable": str(variable_expr),
            "normalized": str(normalized),
            "result": result_text,
            "result_latex": result_latex,
            "chain_latex": " \\Longleftrightarrow ".join(step["latex"] for step in steps if step.get("latex")),
            "steps": steps,
            "solutions": [str(item) for item in solutions],
        }

    left = parse_math_expression(left_text)
    right = parse_math_expression(right_text)
    radical_result = build_radical_equation_result(left, right, left_text, right_text)
    if radical_result:
        result_text, result_latex, steps, solutions, normalized = radical_result
        variable_expr = detect_variable(normalized)
        return {
            "original": f"{left_text}={right_text}",
            "variable": str(variable_expr),
            "normalized": str(normalized),
            "result": result_text,
            "result_latex": result_latex,
            "chain_latex": " \\Longleftrightarrow ".join(step["latex"] for step in steps if step.get("latex")),
            "steps": steps,
            "solutions": [str(item) for item in solutions],
        }

    rational_expr = together(left - right)
    numerator, denominator = fraction(rational_expr)
    variable_expr = detect_variable(rational_expr, variable)
    if denominator != 1 and denominator.has(variable_expr):
        result_text, result_latex, steps, solutions, normalized = build_rational_equation_result(
            left,
            right,
            left_text,
            right_text,
            variable_expr,
        )
        return {
            "original": f"{left_text}={right_text}",
            "variable": str(variable_expr),
            "normalized": str(normalized),
            "result": result_text,
            "result_latex": result_latex,
            "chain_latex": " \\Longleftrightarrow ".join(step["latex"] for step in steps if step.get("latex")),
            "steps": steps,
            "solutions": [str(item) for item in solutions],
        }

    normalized = expand(left - right)
    factored = factor(normalized)
    solution_set = solveset(Eq(left, right), variable_expr, domain=S.Reals)
    solutions = sorted_real_solutions(solution_set)

    polynomial = Poly(normalized, variable_expr)
    if polynomial.degree() == 1:
        result_text, result_latex, steps = build_linear_equation_result(
            left,
            right,
            left_text,
            right_text,
            variable_expr,
            solutions,
        )
        return {
            "original": f"{left_text}={right_text}",
            "variable": str(variable_expr),
            "normalized": str(normalized),
            "result": result_text,
            "result_latex": result_latex,
            "chain_latex": steps[0]["latex"],
            "steps": steps,
            "solutions": [str(item) for item in solutions],
        }

    if polynomial.degree() == 2:
        result_text, result_latex, steps = build_quadratic_equation_result(
            left,
            right,
            left_text,
            right_text,
            variable_expr,
            normalized,
            solutions,
        )
        return {
            "original": f"{left_text}={right_text}",
            "variable": str(variable_expr),
            "normalized": str(normalized),
            "result": result_text,
            "result_latex": result_latex,
            "chain_latex": "",
            "steps": steps,
            "solutions": [str(item) for item in solutions],
        }

    steps = [
        {
            "expression": f"{left_text}={right_text}",
            "explanation": "Записываем исходное уравнение",
            "latex": f"{latex(left)} = {latex(right)}",
        },
        {
            "expression": str(normalized),
            "explanation": "Переносим все слагаемые в левую часть и приводим подобные",
            "latex": f"{latex(normalized)} = 0",
        },
    ]

    if factored != normalized:
        steps.append({
            "expression": str(factored),
            "explanation": "Раскладываем левую часть на множители",
            "latex": f"{latex(factored)} = 0",
        })

    result_latex = solution_latex(variable_expr, solutions)
    steps.append({
        "expression": ", ".join(str(item) for item in solutions) if solutions else "нет действительных корней",
        "explanation": "Получаем корни уравнения",
        "latex": result_latex,
    })

    if not solutions:
        result_text = "нет действительных корней"
    elif len(solutions) == 1:
        result_text = f"{variable_expr} = {solutions[0]}"
    else:
        result_text = "; ".join(
            f"{variable_expr}_{index + 1} = {value}"
            for index, value in enumerate(solutions)
        )

    chain_parts = [f"{latex(left)} = {latex(right)}", f"{latex(normalized)} = 0"]
    if factored != normalized:
        chain_parts.append(f"{latex(factored)} = 0")
    chain_parts.append(result_latex)

    return {
        "original": f"{left_text}={right_text}",
        "variable": str(variable_expr),
        "normalized": str(normalized),
        "result": result_text,
        "result_latex": result_latex,
        "chain_latex": " \\Longleftrightarrow ".join(chain_parts),
        "steps": steps,
        "solutions": [str(item) for item in solutions],
    }
