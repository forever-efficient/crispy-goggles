.PHONY: setup install-browsers test

setup:
	python -m venv .venv
	@echo "Activate with: source .venv/bin/activate"
	. .venv/bin/activate && pip install -e .[dev]

install-browsers:
	@echo "Installing Playwright browsers"
	playwright install

VENV_PYTHON=.venv/bin/python

setup-dev: setup install-browsers
	@echo "Setting up development environment (dev extras + browsers) using $(VENV_PYTHON)"
	@if [ ! -f .venv/bin/activate ]; then \
		python -m venv .venv; \
	fi
	$(VENV_PYTHON) -m pip install --upgrade pip setuptools wheel
	$(VENV_PYTHON) -m pip install -e '.[dev]'
	$(VENV_PYTHON) -m playwright install

pre-commit-install:
	@echo "Installing pre-commit hooks into the venv"
	$(VENV_PYTHON) -m pre_commit install

test: install-browsers
	@echo "Running pytest (Playwright-based tests)"
	. .venv/bin/activate && .venv/bin/python -m pytest -q
