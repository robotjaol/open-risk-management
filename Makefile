.PHONY: install test lint format data fetch-data notebooks build status clean

install:
	pip install -e ".[development]"

test:
	python -m pytest tests -q --ignore=tests/notebook_validation

test-notebooks:
	python -m pytest tests/notebook_validation -q

lint:
	ruff check src tests tools

format:
	ruff format src tests tools

data:
	python tools/build_datasets.py

fetch-data:
	python tools/fetch_real_data.py

build:
	python tools/build_modules.py

notebooks:
	python tools/run_notebooks.py

status:
	python tools/render_status.py

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache
