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
    _define_ast(
        args.path,
        "ast",
        "Expr",
        [
            "Binary   ; left: Expr, operator: Token, right: Expr",
            "Grouping ; expression: Expr",
            "Literal  ; value: object",
            "Unary    ; operator: Token, right: Expr",
        ],
    )


def _define_type(base_name: str, class_name: str, fields_str: str) -> str:
    type_ = f"""class {class_name}({base_name}):
    def __init__(self, {fields_str}) -> None:
"""
    fields = [field.strip() for field in fields_str.split(",")]
    for field in fields:
        field_name = field.split(": ")[0]
        type_ += f"        self.{field_name} = {field_name}\n"

    type_ += "    @override\n"
    type_ += '    def accept[T](self, visitor: "Visitor[T]") -> T:\n'
    type_ += (
        f"        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n"
    )
    return type_


def _define_ast(
    output_dir: Path, file_name: str, base_name: str, types: Sequence[str]
) -> None:
    path = output_dir / f"{file_name}.py"  # TODO: remove file_name param?
    definition = f"""
from lox.scanner import Token
from abc import ABC, abstractmethod
from typing import Protocol, override, TypeVar

T = TypeVar('T')

class {base_name}(ABC):
    @abstractmethod
    def accept[T](self, visitor: \"Visitor[T]\") -> T: ...
"""

    for type_ in types:
        class_name, fields = type_.split(";", maxsplit=1)
        definition += _define_type(base_name, class_name.strip(), fields.strip())

    definition += """

class Visitor[T](ABC):
"""
    for type_ in types:
        class_name, _fields = type_.split(";", maxsplit=1)
        class_name = class_name.strip()
        definition += "      @abstractmethod\n"
        definition += f"      def visit_{class_name.lower()}_{base_name.lower()}(self, expr: {class_name}) -> T: ...\n"

    path.write_text(definition, encoding="utf-8")
    subprocess.run(["uv", "run", "ruff", "check", "--fix"], check=False)
    subprocess.run(["uv", "run", "ruff", "format"], check=False)


if __name__ == "__main__":
    main()
