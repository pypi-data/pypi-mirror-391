.PHONY: help install install-dev build clean test lint format publish docker-up docker-down

help: ## Show this help message
	@echo "🚀 Airflow CLI - Available Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package
	pip install -e .

install-dev: ## Install package with dev dependencies
	pip install -e ".[dev]"

build: ## Build distribution packages
	python -m build
	@echo "✅ Build complete! Check dist/ directory"

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned build artifacts"

test: ## Run tests
	pytest tests/ -v --cov=src --cov-report=term-missing

lint: ## Run linting
	flake8 src/ --max-line-length=120
	@echo "✅ Linting complete"

format: ## Format code with black
	black src/ --line-length=120
	@echo "✅ Code formatted"

format-check: ## Check code formatting
	black src/ --check --line-length=120

publish-test: build ## Publish to TestPyPI
	python -m twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	python -m twine upload dist/*

docker-up: ## Start Airflow environment
	python -m src.cli up

docker-down: ## Stop Airflow environment
	python -m src.cli down

docker-status: ## Check Docker environment status
	python -m src.cli status

dev-setup: install-dev ## Complete dev environment setup
	@echo "✅ Development environment ready!"
	@echo "💡 Run 'make docker-up' to start Airflow"

release: clean lint test build ## Prepare for release
	@echo "✅ Release preparation complete!"
	@echo "💡 Review dist/ and run 'make publish' when ready"