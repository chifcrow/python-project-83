PYTHON := python3
VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
VENV_PY := $(VENV_BIN)/python
PIP := $(VENV_PY) -m pip

.PHONY: help install dev start test lint format check clean

help:
	@echo "Available targets:"
	@echo "  make install
	@echo "  make dev
	@echo "  make start
	@echo "  make test
	@echo "  make lint
	@echo "  make format
	@echo "  make clean

# Create virtual environment
$(VENV_PY):
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "ERROR: python3 is not installed."; exit 1; }
	@$(PYTHON) -c "import venv" >/dev/null 2>&1 || { \
		echo "ERROR: python3-venv is missing. Install it with:"; \
		echo "  sudo apt update && sudo apt install -y python3-venv"; \
		exit 1; \
	}
	@$(PYTHON) -m venv $(VENV_DIR)

install: $(VENV_PY)
	@$(VENV_PY) -c "import ensurepip" >/dev/null 2>&1 || true
	@$(VENV_PY) -m pip --version >/dev/null 2>&1 || { \
		echo "ERROR: pip is not available in the venv."; \
		echo "Try installing system packages:"; \
		echo "  sudo apt update && sudo apt install -y python3-pip python3-venv"; \
		exit 1; \
	}
	@$(PIP) install -U pip setuptools wheel
	@$(PIP) install -e .
	@$(PIP) install flask gunicorn python-dotenv pytest ruff

dev: $(VENV_PY)
	@$(VENV_PY) -m flask --app page_analyzer.app:app run

start: $(VENV_PY)
	@test -n "$(PORT)" || { echo "ERROR: PORT is not set. Example: PORT=8000 make start"; exit 1; }
	@$(VENV_BIN)/gunicorn page_analyzer:app --bind 0.0.0.0:$(PORT)

test: $(VENV_PY)
	@$(VENV_PY) -m pytest -q

lint: $(VENV_PY)
	@$(VENV_PY) -m ruff check .

format: $(VENV_PY)
	@$(VENV_PY) -m ruff format .

check: lint test

clean:
	@rm -rf $(VENV_DIR) .pytest_cache .ruff_cache __pycache__ */__pycache__
