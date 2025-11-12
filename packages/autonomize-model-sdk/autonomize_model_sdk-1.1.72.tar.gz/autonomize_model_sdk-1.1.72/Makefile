GIT_ROOT ?= $(shell git rev-parse --show-toplevel)

install:	## Install dependencies with uv.
	uv sync --all-extras --dev

format:	## Run code autoformatter (black).
	uv run black .

lint:	## Run linters: pre-commit, black, isort, autoflake, etc.
	uv run pre-commit install && uv run pre-commit run --all-files

test:	## Run tests.
	uv run pytest tests

build:	## Build the package.
	uv build

publish:	## Publish to PyPI (requires PYPI token).
	uv publish

dev-install:	## Install package in development mode.
	uv sync --dev

clean:	## Clean build artifacts.
	rm -rf dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage

help:	## Show this help message.
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
