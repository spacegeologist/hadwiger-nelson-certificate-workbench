from __future__ import annotations

import ast
from math import sqrt

from hnp.embedding import Point


class _SafeMathEvaluator(ast.NodeVisitor):
    def visit_Expression(self, node: ast.Expression) -> float:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> float:
        if not isinstance(node.value, int | float):
            raise ValueError(f"unsupported constant: {node.value!r}")
        return float(node.value)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> float:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError(f"unsupported unary operator: {ast.dump(node.op)}")

    def visit_BinOp(self, node: ast.BinOp) -> float:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left**right
        raise ValueError(f"unsupported binary operator: {ast.dump(node.op)}")

    def visit_Call(self, node: ast.Call) -> float:
        if not isinstance(node.func, ast.Name) or node.func.id != "sqrt":
            raise ValueError(f"unsupported function call: {ast.dump(node)}")
        if len(node.args) != 1 or node.keywords:
            raise ValueError("sqrt expects one positional argument")
        return sqrt(self.visit(node.args[0]))

    def generic_visit(self, node: ast.AST) -> float:
        raise ValueError(f"unsupported expression node: {ast.dump(node)}")


def parse_mathematica_number(expression: str) -> float:
    """Parse the small Mathematica-style arithmetic language used by CNP-SAT .vtx files."""

    python_expression = expression.strip().replace("^", "**").replace("Sqrt[", "sqrt(").replace("]", ")")
    tree = ast.parse(python_expression, mode="eval")
    return _SafeMathEvaluator().visit(tree)


def _split_coordinate_pair(line: str, line_number: int) -> tuple[str, str]:
    stripped = line.strip()
    if not stripped.startswith("{") or not stripped.endswith("}"):
        raise ValueError(f"line {line_number}: expected '{{x, y}}' coordinate pair")

    body = stripped[1:-1]
    depth = 0
    for index, character in enumerate(body):
        if character == "(" or character == "[":
            depth += 1
        elif character == ")" or character == "]":
            depth -= 1
            if depth < 0:
                raise ValueError(f"line {line_number}: unbalanced coordinate expression")
        elif character == "," and depth == 0:
            return body[:index].strip(), body[index + 1 :].strip()

    raise ValueError(f"line {line_number}: expected two coordinate expressions")


def parse_vtx_text(text: str) -> dict[str, Point]:
    coordinates: dict[str, Point] = {}
    vertex_index = 1

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        x_expression, y_expression = _split_coordinate_pair(raw_line, line_number)
        coordinates[str(vertex_index)] = (
            parse_mathematica_number(x_expression),
            parse_mathematica_number(y_expression),
        )
        vertex_index += 1

    return coordinates
