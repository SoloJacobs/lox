import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel

from lox.interpret import Interpreter
from lox.parser import Parser
from lox.runtime_error import LoxRuntimeErr
from lox.scanner import Scanner, Token, TokenType


class Args(BaseModel):
    path: Path | None = None


def parse_arguments(args: Sequence[str]) -> Args:
    parser = argparse.ArgumentParser(description="jlox")
    parser.add_argument("path", nargs="?", const=None, help="script to run with jlox")

    return Args.model_validate(vars(parser.parse_args(args)))  # type: ignore[misc]


class Lox:
    def __init__(self) -> None:
        self.had_error = False
        self.had_runtime_error = False
        self._interpreter = Interpreter()

    def error(self, line: int, message: str) -> None:
        self._report(line, "", message)

    def parser_error(self, token: Token, message: str) -> None:
        if token.type_ == TokenType.EOF:
            self._report(token.line, " at end", message)
        else:
            self._report(token.line, f" at '{token.lexeme}'", message)

    def runtime_error(self, err: LoxRuntimeErr) -> None:
        self.had_runtime_error = True
        self._report(err.token.line, "", err.message)

    def _report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        self.had_error = True

    def _run(self, source: str) -> None:
        scanner = Scanner(self, source)  # Ugh
        tokens = scanner.scan_tokens()
        if self.had_error:
            return
        statements = Parser(self, tokens).parse()
        if statements is None:
            return
        self._interpreter.interpret(self, statements)

    def run_file(self, path: Path) -> None:
        source = path.read_text("utf-8")
        self._run(source)
        if self.had_error:
            sys.exit(65)
        if self.had_runtime_error:
            sys.exit(70)

    def run_prompt(self) -> None:
        while True:
            try:
                line = input("> ")
            except EOFError:
                print()
                break
            self._run(line)
            self.had_error = False


def main() -> None:
    args = parse_arguments(sys.argv[1:])
    match args.path:
        case None:
            Lox().run_prompt()
        case path:
            Lox().run_file(path)


if __name__ == "__main__":
    main()
