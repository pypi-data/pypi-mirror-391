# Zephyr Framework - Development Makefile

.PHONY: help install install-dev install-stubs clean test lint format stubs stubs-clean stubs-zephyr stubs-examples stubs-taskflow check-stubs

# Default target
help:
	@echo "🚀 Zephyr Framework Development Commands"
	@echo ""
	@echo "📦 Installation:"
	@echo "  install          Install the package"
	@echo "  install-dev      Install with development dependencies"
	@echo "  install-stubs    Install with stub generation dependencies"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  clean            Clean build artifacts and cache"
	@echo "  stubs-clean      Clean generated stub files"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  test             Run tests"
	@echo "  lint             Run linting (ruff + mypy)"
	@echo "  format           Format code (black + isort + ruff)"
	@echo ""
	@echo "📝 Stub Generation:"
	@echo "  stubs            Generate all stub files"
	@echo "  stubs-zephyr     Generate Zephyr framework stubs only"
	@echo "  stubs-examples   Generate example application stubs only"
	@echo "  stubs-taskflow   Generate TaskFlow OIDC example stubs only"
	@echo "  check-stubs      Validate generated stub files"
	@echo ""

# Installation targets
install:
	@echo "📦 Installing Zephyr framework..."
	pip install -e .

install-dev:
	@echo "📦 Installing Zephyr with development dependencies..."
	pip install -e ".[dev]"

install-stubs:
	@echo "📦 Installing Zephyr with stub generation dependencies..."
	pip install -e ".[dev,stubs]"

# Cleanup targets
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

stubs-clean:
	@echo "🧹 Cleaning generated stub files..."
	rm -rf stubs/

# Testing and quality targets
test:
	@echo "🧪 Running tests..."
	uv run pytest

lint:
	@echo "🔍 Running linting..."
	uv run ruff check .
	uv run mypy .

format:
	@echo "✨ Formatting code..."
	uv run black .
	uv run isort .
	uv run ruff format .

# Stub generation targets
stubs: install-stubs
	@echo "📝 Generating all stub files..."
	uv run python scripts/generate_stubs.py --clean

stubs-zephyr: install-stubs
	@echo "📝 Generating Zephyr framework stubs..."
	uv run python scripts/generate_stubs.py --zephyr-only --clean

stubs-examples: install-stubs
	@echo "📝 Generating example application stubs..."
	uv run python scripts/generate_stubs.py --examples-only --clean

stubs-taskflow: install-stubs
	@echo "📝 Generating TaskFlow OIDC example stubs..."
	uv run python scripts/generate_stubs.py --taskflow-only --clean

check-stubs:
	@echo "✅ Validating generated stub files..."
	@if [ -d "stubs" ]; then \
		echo "📂 Found stub files:"; \
		find stubs -name "*.pyi" | head -10; \
		echo "🔍 Running mypy on stub files..."; \
		uv run mypy stubs/ --ignore-missing-imports || true; \
	else \
		echo "❌ No stub files found. Run 'make stubs' first."; \
	fi

# Development workflow
dev-setup: install-dev
	@echo "🛠️  Development environment setup complete!"
	@echo "💡 Next steps:"
	@echo "  - Run 'make stubs' to generate stub files"
	@echo "  - Run 'make test' to run tests"
	@echo "  - Run 'make lint' to check code quality"

# Quick development cycle
dev-cycle: format lint test
	@echo "✅ Development cycle complete!"

# CI/CD targets
ci: install-dev lint test
	@echo "🚀 CI pipeline complete!"
