# Identify_gCNV_with_WES

## Overview
This directory contains the core implementation of the CNV detection workflow in this repository. It uses Snakemake to manage CNV analysis from whole-exome sequencing (WES). The entry points are `starpro_github/workflow/Snakefile` and `starpro_github/workflow/config.yaml`, with `scripts/agents/` providing helper scripts for plan generation, execution, QC, and publishing.

## Repository layout
- `workflow/`: Snakemake `Snakefile`, `config.yaml`, tests, and workflow resources
- `scripts/`: Helper scripts (download, preprocessing, visualization, etc.)
- `scripts/agents/`: Plan, run, QC, publish, and other agent scripts
- `data/`: Reference genomes, interval lists, BAM files, annotation files, and other data
- `model/`: Pre-trained models
- `plans/`: Example plan files
- `outputs/`: Suggested output directory for results

## Quick Start

### 1. Install Dependencies
Conda is recommended:
```bash
cd starpro_github
conda env create -f environment.yml
conda activate cnv_workflow
```

If you prefer Docker, see the "Docker Usage" section.

### 2. Download Annotation Resources
```bash
cd starpro_github
bash scripts/download_zenodo_data.sh
```

### 3. Generate Per-Sample Plan Files
It is recommended to use plan files to drive the workflow. Example plan files are located in the root directory `plans/EXAMPLE.plan.yaml` or in this directory `starpro_github/plans/example.plan.yaml`.

Run the plan generation script from `starpro_github/`:
```bash
cd starpro_github
python scripts/agents/plan_agent.py --sample HG00099 --bam ../data/bam/HG00099.recal.bam --out ../plans/HG00099.plan.yaml
```

This script reads default values from `starpro_github/workflow/config.yaml` and generates a plan file that can be used directly with Snakemake.

### 4. Run Snakemake
Execute from the `starpro_github/` directory. The default workflow prioritizes plan files in `plans/`, falling back to `data/bam/*.bam` if no plans are found.

Dry-run to verify:
```bash
cd starpro_github
snakemake --snakefile workflow/Snakefile --configfile ../plans/EXAMPLE.plan.yaml -n
```

Execute formally:
```bash
cd starpro_github
snakemake --snakefile workflow/Snakefile --configfile ../plans/EXAMPLE.plan.yaml --cores 4
```

If using the example plan in this directory:
```bash
cd starpro_github
snakemake --snakefile workflow/Snakefile --configfile plans/example.plan.yaml --cores 4
```

## Execution Logic

### Plan Mode
Prioritizes per-sample plan files in `plans/`. Plan files specify sample name, BAM path, reference sequence, interval list, model path, GATK command, work directory, and other information.

### Direct BAM Mode
If no plan files exist in `plans/`, the Snakefile automatically scans `data/bam/*.bam` and generates default inputs based on sample names. This mode is suitable for quick tests or simple data structures, but plan files are recommended for explicit path and parameter management.

### Configuration File Description
Main configuration file: `starpro_github/workflow/config.yaml`

This file includes:
- Reference genome, dictionary, interval list, model paths
- Tool command names like GATK, BWA, samtools, Picard
- Visualization tools and annotation resource paths

`plan_agent.py` reads defaults from this file to generate plan files, facilitating consistent paths across different machines.

## Agents Usage Examples

- Generate a plan:
```bash
cd starpro_github
python scripts/agents/plan_agent.py --sample HG00099 --bam ../data/bam/HG00099.recal.bam --out ../plans/HG00099.plan.yaml
```

- Validate and print the run command:
```bash
cd starpro_github
python scripts/agents/run_agent.py --plan ../plans/HG00099.plan.yaml --cores 2
```

- Execute the plan directly:
```bash
cd starpro_github
python scripts/agents/run_agent.py --plan ../plans/HG00099.plan.yaml --cores 4 --execute
```

- Generate QC report:
```bash
cd starpro_github
python scripts/agents/qc_agent.py --plan ../plans/HG00099.plan.yaml --out ../outputs/HG00099.qc.yaml
```

- Package for publishing:
```bash
cd starpro_github
python scripts/agents/publish_agent.py --plan ../plans/HG00099.plan.yaml --out-dir ../outputs/publish/HG00099 --package
```

## Docker Usage

To use Docker, build the image in the `starpro_github/` directory:
```bash
cd starpro_github
docker build -t cnv-detection .
```

Recommended: Mount the entire repository and run inside the container:
```bash
docker run --rm -it \
  -v $(pwd):/workspace \
  -w /workspace/starpro_github \
  cnv-detection \
  bash -lc "snakemake --snakefile workflow/Snakefile --configfile workflow/config.yaml -n"
```

Mount only necessary directories:
```bash
docker run --rm -it \
  -v $(pwd)/starpro_github:/workspace \
  -v $(pwd)/data:/workspace/data \
  -v $(pwd)/plans:/workspace/plans \
  -v $(pwd)/outputs:/workspace/outputs \
  -w /workspace \
  cnv-detection \
  bash -lc "snakemake --snakefile workflow/Snakefile --configfile workflow/config.yaml --cores 4"
```

### Docker Tips
- Avoid packaging large data files into the image; mount `data/`, `plans/`, `outputs/` externally.
- Paths in `workflow/config.yaml` are typically relative, so use `starpro_github/` as the container working directory.

## Common Commands
- Create Conda environment: `make env-conda`
- Create local venv: `make env-venv`
- Run smoke tests: `make smoke`
- Snakemake dry-run: `make snakemake-dry`
- Build Docker image: `make docker-build`
- Run Docker: `make docker-run`

## Other Notes
- When using `plans/` mode, ensure that `bam` and `workpath` entries in the plan point to correct files or directories.
- Modify `starpro_github/workflow/config.yaml` according to your local environment for tool command names and resource paths.
- `starpro_github/scripts/agents/plan_agent.py` checks BAM file size and provides notes for small BAM files.

## License
This project is licensed under the MIT License.