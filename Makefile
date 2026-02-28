RUNS ?= 10

.PHONY: clean
clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete


.PHONY: test
test:
	@uv run python -c 'import yaml; print("model:", yaml.safe_load(open("config.yaml","r",encoding="utf-8"))["agent"]["model"])'
	@seq 1 $(RUNS) | \
	xargs -P$(RUNS) -I{} uv run -m src.main | \
	awk -F': ' '/^score: [0-9]+$$/ { sum += $$2; n++ } END { if (n) printf("runs=%d avg=%.4f\n", n, sum/n) }'
