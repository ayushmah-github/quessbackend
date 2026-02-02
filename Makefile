.PHONY: help setup install run test lint format clean docker-build docker-run stop

help:
	@echo "HRMS Backend - Available Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup      - Create virtual environment and install dependencies"
	@echo "  make install    - Install/upgrade dependencies"
	@echo ""
	@echo "Running:"
	@echo "  make run        - Start development server"
	@echo "  make run-prod   - Start production server (gunicorn)"
	@echo ""
	@echo "Testing:"
	@echo "  make test       - Run all tests"
	@echo "  make test-v     - Run tests with verbose output"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint       - Run linting checks"
	@echo "  make format     - Format code with black"
	@echo ""
	@echo "Database:"
	@echo "  make clean-db   - Remove SQLite database"
	@echo "  make reset-db   - Reset database (recreate)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean      - Remove cache files and directories"
	@echo "  make clean-all  - Remove virtual environment and cache"

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

install:
	. venv/bin/activate && pip install -r requirements.txt

run:
	. venv/bin/activate && python3 -m uvicorn HrmsBackend.main:app --reload --port 8000

run-prod:
	. venv/bin/activate && pip install gunicorn && \
	gunicorn -w 4 -k uvicorn.workers.UvicornWorker HrmsBackend.main:app --bind 0.0.0.0:8000

test:
	. venv/bin/activate && pip install -r requirements-dev.txt && pytest tests/

test-v:
	. venv/bin/activate && pip install -r requirements-dev.txt && pytest tests/ -v

lint:
	. venv/bin/activate && pip install flake8 && flake8 HrmsBackend/

format:
	. venv/bin/activate && pip install black && black HrmsBackend/

clean-db:
	rm -f hrms.db

reset-db: clean-db
	@echo "Database will be recreated on next server start"

docker-build:
	docker build -t hrms-backend:latest .

docker-run:
	docker run -p 8000:8000 -v $(PWD)/hrms.db:/app/hrms.db hrms-backend:latest

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/ .coverage/ htmlcov/

clean-all: clean
	rm -rf venv/
	rm -f hrms.db

.DEFAULT_GOAL := help
