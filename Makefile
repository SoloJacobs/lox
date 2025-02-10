.PHONY: help setup format lint test dependency-update dependency-add all-checks
help:
	@echo "setup             --> Prepare virtual environment for development and benchmarks submodule"
	@echo "format            --> Run formatters (TOML, python)"
	@echo "lint              --> Run linters (mypy, ruff)"
	@echo "test              --> Run test targets"
	@echo "all-checks        --> Check prerequisites for merging"
	@echo "dependency-update --> Update dependencies in requirementes.txt, uv.lock"
	@echo "dependency-add    --> Add new dependency; must pass 'args=ARGS' such that 'uv add ARGS' is valid"

setup:
	uv venv
	uv sync

format:
	uv run ruff format
	uv run taplo format pyproject.toml

lint:
	uv run ruff check
	uv run ruff format --diff
	uv run taplo format --diff
	uv run mypy

test:
	uv run pytest

dependency-update:
	uv sync --upgrade
	uv pip compile pyproject.toml -o requirements.txt
	uv run taplo format pyproject.toml

dependency-add:
	uv add $(args)
	uv pip compile pyproject.toml -o requirements.txt
	uv run taplo format pyproject.toml

all-checks: test lint
