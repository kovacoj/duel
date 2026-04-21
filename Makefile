RUNS ?= 3
DATASET ?= examples/replay_sample.json
PROVIDER ?= oracle

.PHONY: clean
clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache



.PHONY: benchmark
benchmark:
	uv run python -m src.main benchmark --source replay --dataset $(DATASET) --provider $(PROVIDER) --runs $(RUNS)


.PHONY: report
report:
	uv run python -m src.main report


.PHONY: lint
lint:
	uv run ruff check .


.PHONY: test
test:
	uv run pytest
