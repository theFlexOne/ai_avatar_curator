.PHONY: setup clean lint test scrape process enforce-immutable-raw ui

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	mkdir -p data/raw data/processed src

clean:
	rm -rf __pycache__ .pytest_cache .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +

scrape:
	. .venv/bin/activate && python -m dotenv run -- python -m src.scrape "$(SUBJECT)"

process: enforce-immutable-raw
	. .venv/bin/activate && python -m src.process $(SUBJECT)

ui:
	. .venv/bin/activate && PYTHONPATH=. streamlit run src/ui/app.py

lint:
	. .venv/bin/activate && ruff check .

test:
	. .venv/bin/activate && pytest tests/

enforce-immutable-raw:
	. .venv/bin/activate && python scripts/enforce_read_only.py data/raw
