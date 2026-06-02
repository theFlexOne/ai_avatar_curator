.PHONY: setup clean lint test

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	mkdir -p data/raw data/processed src

clean:
	rm -rf __pycache__ .pytest_cache .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	ruff check .

test:
	pytest tests/
