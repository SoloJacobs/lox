from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    pass


def scan_tokens(source: str) -> list[Token]:
    raise NotImplementedError()
