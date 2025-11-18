.PHONY: help install install-dev test clean build format lint check run
.DEFAULT_GOAL := help

PYTHON := python
UV := uv
PACKAGE_NAME := pln-search

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install package in development mode
	$(UV) pip install -e .

install-dev: ## Install with dev dependencies
	$(UV) pip install -e ".[dev]"
	$(UV) add --dev pytest pytest-mock requests-mock ruff

test: ## Run tests
	$(PYTHON) -m pytest tests/ -v

test-coverage: ## Run tests with coverage
	$(UV) add --dev coverage
	coverage run -m pytest tests/
	coverage report
	coverage html

lint: ## Run linting
	$(UV) run ruff check .

format: ## Format code
	$(UV) run ruff format .

lint-fix: ## Run linting with auto-fix
	$(UV) run ruff check . --fix

check: lint test ## Run linting and tests

check-fix: lint-fix format test ## Fix lint issues, format, and test

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/
	rm -rf .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution
	$(UV) build

check-version: ## Check if version needs to be updated for PyPI
	@echo "Current version in pyproject.toml:"
	@grep "^version" pyproject.toml
	@echo ""
	@echo "Latest version on PyPI (if package exists):"
	@python -m pip index versions $(PACKAGE_NAME) 2>/dev/null || echo "Package not found on PyPI (this is normal for new packages)"

upload-test: build ## Upload to TestPyPI
	$(UV) pip install twine
	$(UV) run twine check dist/*
	$(UV) run twine upload --repository testpypi dist/*
	@echo ""
	@echo "Test installation with:"
	@echo "pip install --index-url https://test.pypi.org/simple/ $(PACKAGE_NAME)"

upload: build ## Upload to PyPI (production)
	$(UV) pip install twine
	$(UV) run twine check dist/*
	@echo "About to upload to PyPI. This cannot be undone!"
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ]
	$(UV) run twine upload dist/*

run: ## Run pln-search (development)
	$(UV) run pln-search

auth: ## Run authentication flow
	$(UV) run pln-search auth login

auth-status: ## Check auth status
	$(UV) run pln-search auth status

search-test: ## Run a test search (requires auth)
	$(UV) run pln-search --members "test"

dev-setup: install-dev ## Complete development setup
	@echo "Development environment ready!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make check' to run linting and tests"
