IMAGE := todotxt-test

.PHONY: test lint deploy

test:
	docker build -t $(IMAGE) .
	docker run --rm -v "$$(pwd)":/app $(IMAGE) sh -c "python3 -m pytest tests/ -v && ruff check src/ tests/"

lint:
	docker build -t $(IMAGE) .
	docker run --rm -v "$$(pwd)":/app $(IMAGE) sh -c "ruff check src/ tests/ && ruff format --check src/ tests/"

deploy:
	@echo "todotxt is a local CLI tool — no remote deployment configured."
