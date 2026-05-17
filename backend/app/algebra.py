import re

from sympy import Add, simplify, expand, factor, cancel, fraction, latex
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def normalize_mixed_numbers(expression: str) -> str:
    def replace_match(match):
        whole = int(match.group(1))
        numerator = match.group(2)
        denominator = match.group(3)
        sign = "+" if whole >= 0 else "-"
        return f"({whole}{sign}{numerator}/{denominator})"

    return re.sub(r"(?<![\w.])(-?\d+)\s*\(\s*(\d+)\s*/\s*(\d+)\s*\)", replace_match, expression)


def find_matching_parenthesis(text: str, open_index: int) -> int:
    depth = 0
    for index in range(open_index, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return index
    return -1


def normalize_logarithms(expression: str) -> str:
    result = []
    index = 0

    while index < len(expression):
        if expression.startswith("log_", index):
            base_start = index + 4
            argument_start = expression.find("(", base_start)
            if argument_start == -1:
                result.append(expression[index])
                index += 1
                continue

            base = expression[base_start:argument_start].strip()
            argument_end = find_matching_parenthesis(expression, argument_start)
            if not base or argument_end == -1:
                result.append(expression[index])
                index += 1
                continue

            argument = expression[argument_start + 1:argument_end]
            result.append(
                f"log(({normalize_logarithms(argument)}),({normalize_logarithms(base)}))"
            )
            index = argument_end + 1
            continue

        result.append(expression[index])
        index += 1

    return "".join(result)


def parse_math_expression(expression: str):
    prepared = normalize_logarithms(normalize_mixed_numbers(expression.strip().replace("÷", "/")))
    return parse_expr(prepared, transformations=TRANSFORMATIONS, evaluate=False)


def make_step(expr, explanation: str):
    return {
        "expression": str(expr),
        "explanation": explanation,
        "latex": latex(expr),
    }


def input_to_latex(expression: str) -> str:
    prepared = expression.strip().replace("*", "")
    prepared = prepared.replace(" ", "")
    prepared = prepared.replace("^", "^{")

    result = []
    i = 0
    while i < len(prepared):
        ch = prepared[i]
        if ch == "{" and result and result[-1] == "^":
            result.append(ch)
            i += 1
            continue
        if len(result) >= 2 and result[-2] == "^" and result[-1] == "{" and ch.isdigit():
            digits = []
            while i < len(prepared) and prepared[i].isdigit():
                digits.append(prepared[i])
                i += 1
            result.append("".join(digits))
            result.append("}")
            continue
        result.append(ch)
        i += 1

    return "".join(result)


def term_latex(term, first=False):
    text = latex(term)
    if text.startswith("-"):
        return f"-{text[1:].strip()}"
    return text if first else f"+{text}"


def expanded_without_collecting(expr):
    source_terms = expr.args if isinstance(expr, Add) else (expr,)
    terms = []

    for source_term in source_terms:
        expanded = expand(source_term)
        if isinstance(expanded, Add):
            terms.extend(expanded.as_ordered_terms())
        else:
            terms.append(expanded)

    if not terms:
        return ""

    return "".join(term_latex(term, first=index == 0) for index, term in enumerate(terms))


def build_fraction_chain(original_expr, simplified_expr):
    numerator, denominator = fraction(original_expr)
    if denominator == 1:
        return None

    factored_numerator = factor(numerator)
    factored_denominator = factor(denominator)
    parts = [latex(original_expr)]
    factored_latex = f"\\frac{{{latex(factored_numerator)}}}{{{latex(factored_denominator)}}}"
    final_latex = latex(simplified_expr)

    if factored_latex not in parts:
        parts.append(factored_latex)
    if final_latex not in parts:
        parts.append(final_latex)

    return {
        "expression": " = ".join(parts),
        "explanation": (
            "В числителе выносим общий множитель за скобки, "
            "знаменатель сворачиваем по формуле квадрата суммы, "
            "затем сокращаем одинаковые скобки"
        ),
        "latex": " = ".join(parts),
        "is_chain": True,
    }


def build_simplify_steps(expression: str):
    original_expr = parse_math_expression(expression)

    expanded_expr = expand(original_expr)
    cancelled_expr = cancel(expanded_expr)
    simplified_expr = simplify(cancelled_expr)
    factored_expr = factor(simplified_expr)

    final_result = str(simplified_expr)
    final_result_latex = latex(simplified_expr)

    fraction_chain = build_fraction_chain(original_expr, simplified_expr)
    if fraction_chain:
        steps = [fraction_chain]
    else:
        original_latex = input_to_latex(expression)
        expanded_chain_latex = expanded_without_collecting(original_expr)
        chain_parts = [original_latex]

        if expanded_chain_latex and expanded_chain_latex != original_latex:
            chain_parts.append(expanded_chain_latex)

        if final_result_latex not in chain_parts:
            chain_parts.append(final_result_latex)

        steps = [{
            "expression": " = ".join(str(part) for part in chain_parts),
            "explanation": "Раскрываем скобки, приводим подобные слагаемые и получаем ответ",
            "latex": " = ".join(chain_parts),
            "is_chain": True,
        }]

    detailed_steps = []

    detailed_steps.append(make_step(original_expr, "Исходное выражение"))

    if expanded_expr != original_expr:
        detailed_steps.append(
            make_step(expanded_expr, "Раскрываем скобки и упрощаем запись")
        )

    if cancelled_expr != expanded_expr:
        detailed_steps.append(
            make_step(cancelled_expr, "Сокращаем дроби и упрощаем рациональное выражение")
        )

    if simplified_expr != cancelled_expr:
        detailed_steps.append(
            make_step(simplified_expr, "Упрощаем выражение")
        )

    if factored_expr != simplified_expr:
        detailed_steps.append(
            make_step(factored_expr, "Дополнительно приводим выражение к компактному виду")
        )

    if len(detailed_steps) == 1:
        detailed_steps.append(make_step(simplified_expr, "Выражение уже находится в упрощённом виде"))

    return str(original_expr), final_result, final_result_latex, steps


def evaluate_expression(expression: str, variable: str, value: str):
    simplified = simplify(cancel(expand(parse_math_expression(expression))))
    variable_expr = parse_expr(variable.strip(), transformations=TRANSFORMATIONS)
    value_expr = parse_expr(str(value).strip(), transformations=TRANSFORMATIONS)
    substituted = simplified.subs(variable_expr, value_expr)
    result = simplify(substituted)

    return {
        "variable": str(variable_expr),
        "value": str(value_expr),
        "value_latex": latex(value_expr),
        "expression": str(simplified),
        "expression_latex": latex(simplified),
        "result": str(result),
        "result_latex": latex(result),
        "chain_latex": f"{latex(simplified)}\\big|_{{{latex(variable_expr)}={latex(value_expr)}}} = {latex(result)}",
    }
