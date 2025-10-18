.PHONY: install dev run loop optimizer sims clean

VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
UVICORN=$(VENV)/bin/uvicorn

install:
	@echo "🔧 Creating virtual environment and installing dependencies..."
	python3 -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	@echo "✅ Installation complete."

run:
	@echo "🚀 Starting FastAPI Hub..."
	$(UVICORN) hub.app:app --host 0.0.0.0 --port 8080 --reload

loop:
	@echo "♻️  Starting scheduler loop..."
	PYTHONPATH=. $(PY) hub/scheduler_loop.py

optimizer:
	@echo "🧮 Running standalone optimizer..."
	$(PY) optimizer/solver.py --once

sims:
	@echo "🧪 Running simulation scripts..."
	$(PY) sims/synthetic_ci.py
	$(PY) sims/replay_eval.py

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf $(VENV) __pycache__ */__pycache__ *.pyc .pytest_cache
