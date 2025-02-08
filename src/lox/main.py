import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel


class Args(BaseModel):
    path: Path | None = None


def parse_arguments(args: Sequence[str]) -> Args:
    parser = argparse.ArgumentParser(description="jlox")
    parser.add_argument("path", nargs="?", const=None, help="script to run with jlox")

    return Args.model_validate(vars(parser.parse_args(args)))  # type: ignore[misc]


def run_file(path: Path) -> None:
    pass


def run_prompt() -> None:
    pass


def main() -> None:
    args = parse_arguments(sys.argv[1:])
    match args.path:
        case None:
            run_prompt()
        case path:
            run_file(path)


if __name__ == "__main__":
    main()
