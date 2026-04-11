# Makefile for common developer tasks

.PHONY: env-conda env-venv smoke snakemake-dry docker-build docker-run

# Create conda environment from environment.yml
env-conda:
	@echo "Creating conda env from environment.yml..."
	conda env create -f environment.yml || echo "If conda fails, install mamba or use Docker."

# Create a lightweight Python venv and install Snakemake via pip
env-venv:
	@echo "Creating .venv and installing snakemake (pip)..."
	python3 -m venv .venv
	. .venv/bin/activate && python -m pip install --upgrade pip setuptools && python -m pip install snakemake

# Run smoke harness using system Python
smoke:
	python3 tests/smoke/run_smoke.py

# Snakemake dry-run for the smoke Snakefile
snakemake-dry:
	snakemake --snakefile workflow/smoke/Snakefile -n

# Build a lightweight Docker image (expects Dockerfile present)
docker-build:
	docker build -t cnv-workflow .

# Run smoke target inside container (mount current repo)
docker-run:
	docker run --rm -v $(PWD):/workspace -w /workspace cnv-workflow make smoke
