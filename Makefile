.PHONY: setup clean lint test scrape

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	mkdir -p data/raw data/processed src

clean:
	rm -rf __pycache__ .pytest_cache .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +

scrape:
	. .venv/bin/activate && python -m src.scrape $(SUBJECT)

lint:
	. .venv/bin/activate && ruff check .

test:
	. .venv/bin/activate && pytest tests/
