test:
	poetry run pytest tests/ --cov=scholarSparkObservability --cov-report=term-missing

format:
	poetry run black .
	poetry run isort .

typecheck:
	poetry run mypy src/

lint: format typecheck

build:
	poetry build

.PHONY: test format typecheck lint build