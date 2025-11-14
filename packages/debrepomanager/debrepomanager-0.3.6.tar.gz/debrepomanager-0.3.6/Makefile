.PHONY: help install install-dev test test-verbose test-coverage test-integration lint format type-check clean docs

help:
	@echo "Debian Repository Manager - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        - Install package"
	@echo "  make install-dev    - Install package with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run unit tests"
	@echo "  make test-verbose      - Run tests with verbose output"
	@echo "  make test-coverage     - Run tests with coverage report"
	@echo "  make test-integration  - Run integration tests (Docker required)"
	@echo "  make test-real-apt     - Run REAL apt tests with nginx (Docker required)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           - Run flake8 linter"
	@echo "  make format         - Format code with black"
	@echo "  make format-check   - Check code formatting without changes"
	@echo "  make type-check     - Run mypy type checker"
	@echo "  make check-all      - Run all checks (format, lint, type-check, tests)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove build artifacts and cache files"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-verbose:
	pytest -vv

test-coverage:
	pytest --cov=debrepomanager --cov-report=term-missing --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

test-integration:
	@echo "Running integration tests in Docker..."
	cd tests/integration && docker compose up --build --abort-on-container-exit
	cd tests/integration && docker compose down -v

test-real-apt:
	@echo "Running REAL APT integration tests with nginx..."
	cd tests/integration && docker compose -f docker-compose.realtest.yml up --build --abort-on-container-exit
	cd tests/integration && docker compose -f docker-compose.realtest.yml down -v

lint:
	flake8 debrepomanager/

format:
	black debrepomanager/ tests/

format-check:
	black --check debrepomanager/ tests/

type-check:
	mypy debrepomanager/

check-all: format-check lint type-check test
	@echo "All checks passed!"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete



