.PHONY: setup install-browsers test

setup:
	python -m venv .venv
	@echo "Activate with: source .venv/bin/activate"
	. .venv/bin/activate && pip install -e .[dev]

install-browsers:
	@echo "Installing Playwright browsers"
	playwright install

test: install-browsers
	behave
