import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel


class Args(BaseModel):
    path: Path


def parse_arguments(args: Sequence[str]) -> Args:
    parser = argparse.ArgumentParser(description="generate_ast")
    parser.add_argument("path", help="output directory")

    return Args.model_validate(vars(parser.parse_args(args)))  # type: ignore[misc]


def main() -> None:
    args = parse_arguments(sys.argv[1:])
    path = args.path / "ast.py"
    imports_expr, definition_expr = _define_ast(
        "Expr",
        [
            "Binary   ; left: Expr, operator: Token, right: Expr",
            "Grouping ; expression: Expr",
            "Literal  ; value: object",
            "Unary    ; operator: Token, right: Expr",
        ],
    )
    imports_stmt, definition_stmt = _define_ast(
        "Stmt",
        [
            "Expression ; expression: Expr",
            "Print      ; expression: Expr",
        ],
    )
    file_content = "\n".join(
        (imports_stmt, imports_expr, definition_expr, definition_stmt)
    )
    path.write_text(file_content, encoding="utf-8")
    subprocess.run(["uv", "run", "ruff", "check", "--fix"], check=False)
    subprocess.run(["uv", "run", "ruff", "format"], check=False)


def _define_type(base_name: str, class_name: str, fields_str: str) -> str:
    type_ = f"""
@dataclass(frozen = True)
class {class_name}({base_name}):
"""
    fields = [field.strip() for field in fields_str.split(",")]
    for field in fields:
        type_ += f"    {field}\n"

    type_ += "    @override\n"
    type_ += f'    def accept[T](self, visitor: "Visitor{base_name}[T]") -> T:\n'
    type_ += (
        f"        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n"
    )
    return type_


def _define_ast(base_name: str, types: Sequence[str]) -> tuple[str, str]:
    imports = """
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override, TypeVar

from lox.scanner import Token
"""
    definition = f"""
class {base_name}(ABC):
    @abstractmethod
    def accept[T](self, visitor: \"Visitor{base_name}[T]\") -> T: ...
"""

    for type_ in types:
        class_name, fields = type_.split(";", maxsplit=1)
        definition += _define_type(base_name, class_name.strip(), fields.strip())

    definition += f"""

class Visitor{base_name}[T](ABC):
"""
    for type_ in types:
        class_name, _fields = type_.split(";", maxsplit=1)
        class_name = class_name.strip()
        definition += "      @abstractmethod\n"
        definition += f"      def visit_{class_name.lower()}_{base_name.lower()}(self, expr: {class_name}) -> T: ...\n"
    return imports, definition


if __name__ == "__main__":
    main()
