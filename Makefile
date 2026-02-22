.PHONY: test lint deploy

test:
	python3 -m pytest tests/ -v
	ruff check src/ tests/

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

deploy:
	@echo "todotxt is a local CLI tool — no remote deployment configured."
