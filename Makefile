.PHONY: install sample train evaluate score dashboard test lint format monitor api visuals

PYTHON ?= python3

install:
	$(PYTHON) -m pip install -r requirements.txt

sample:
	$(PYTHON) -m src.make_sample

train:
	$(PYTHON) -m src.train_model

evaluate:
	$(PYTHON) -m src.evaluate

score:
	$(PYTHON) -m src.scoring

monitor:
	$(PYTHON) -m src.monitoring

visuals:
	$(PYTHON) scripts/generate_readme_assets.py

dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py

api:
	$(PYTHON) -m uvicorn api.main:app --reload

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .
