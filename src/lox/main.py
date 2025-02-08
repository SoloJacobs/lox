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


def run(source: str) -> None:
    tokens = scan_tokens(source)
    for token in tokens:
        print(token)


def run_file(path: Path) -> None:
    source = path.read_text()
    run(source)


def run_prompt() -> None:
    while True:
        try:
            line = input("> ")
        except EOFError:
            print()
            break
        run(line)


def main() -> None:
    args = parse_arguments(sys.argv[1:])
    match args.path:
        case None:
            run_prompt()
        case path:
            run_file(path)


if __name__ == "__main__":
    main()
