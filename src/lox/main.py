import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel

from lox.scanner import scan_tokens


class Args(BaseModel):
    path: Path | None = None


def parse_arguments(args: Sequence[str]) -> Args:
    parser = argparse.ArgumentParser(description="jlox")
    parser.add_argument("path", nargs="?", const=None, help="script to run with jlox")

    return Args.model_validate(vars(parser.parse_args(args)))  # type: ignore[misc]


class Lox:
    def __init__(self) -> None:
        self.had_error = False

    def error(self, line: int, message: str) -> None:
        self._report(line, "", message)

    def _report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        self.had_error = True

    def _run(self, source: str) -> None:
        tokens = scan_tokens(source)
        for token in tokens:
            print(token)

    def run_file(self, path: Path) -> None:
        source = path.read_text()
        self._run(source)
        if self.had_error:
            sys.exit(65)

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
