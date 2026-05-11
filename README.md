# Identify_gCNV_with_WES

## Overview
This directory contains the core implementation of the CNV detection workflow in this repository. It uses Snakemake to manage CNV analysis from whole-exome sequencing (WES). The entry points are `./workflow/Snakefile` and `./workflow/config.yaml`, with `scripts/agents/` providing helper scripts for plan generation, execution, QC, and publishing.

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
cd Identify_gCNV_with_WES/
conda env create -f environment.yml
conda activate cnv_workflow
```

If you prefer Docker, see the "Docker Usage" section.

### 2. Download Annotation Resources
```bash
cd Identify_gCNV_with_WES/
bash scripts/download_zenodo_data.sh
```

### 3. Generate Per-Sample Plan Files
It is recommended to use plan files to drive the workflow. Example plan files are located in the root directory `plans/EXAMPLE.plan.yaml` or in this directory `Identify_gCNV_with_WES/plans/example.plan.yaml`.

Run the plan generation script from `Identify_gCNV_with_WES/`:
```bash
cd Identify_gCNV_with_WES
python scripts/agents/plan_agent.py --sample HG00099 --bam ../data/bam/HG00099.recal.bam --out ../plans/HG00099.plan.yaml
```

This script reads default values from `Identify_gCNV_with_WES/workflow/config.yaml` and generates a plan file that can be used directly with Snakemake.

### 4. Run Snakemake
Execute from the `Identify_gCNV_with_WES/` directory. The default workflow prioritizes plan files in `plans/`, falling back to `data/bam/*.bam` if no plans are found.

Dry-run to verify:
```bash
cd Identify_gCNV_with_WES
snakemake --snakefile workflow/Snakefile --configfile ../plans/EXAMPLE.plan.yaml -n
```

Execute formally:
```bash
cd Identify_gCNV_with_WES
snakemake --snakefile workflow/Snakefile --configfile ../plans/EXAMPLE.plan.yaml --cores 4
```

If using the example plan in this directory:
```bash
cd Identify_gCNV_with_WES
snakemake --snakefile workflow/Snakefile --configfile plans/example.plan.yaml --cores 4
```

## Execution Logic

### Two Workflow Modes

This workflow supports two primary modes of execution:

#### Mode 1: CNV Detection with Pre-trained Models (Recommended for most users)
Use pre-trained baseline and ploidy models stored in `model/baseline-model` and `model/ploidy-model` to call CNVs on new samples.

**When to use:** When you have trained models and want to identify CNVs in new samples.

**Typical workflow:**
```bash
cd Identify_gCNV_with_WES
python scripts/agents/plan_agent.py --sample HG00099 --bam ../data/bam/HG00099.recal.bam --out ../plans/HG00099.plan.yaml
snakemake --snakefile workflow/Snakefile --configfile ../plans/HG00099.plan.yaml --cores 4
```

The workflow will:
1. Preprocess BAM files (alignment, duplicate marking, BQSR)
2. Collect read counts using the interval list
3. Use the pre-trained models to call CNVs
4. Perform joint segmentation across samples using GATK JointGermlineCNVSegmentation and the project pedigree file
5. Annotate clustered CNV calls with AnnotSV
6. Generate visualization outputs (knotAnnotSV, vcf2circos, PlotCNV/HandyCNV placeholders)

#### Mode 2: Model Training + CNV Detection
Train models from scratch using control samples, then perform CNV detection on query samples.

**When to use:** When you want to train population-specific or cohort-specific models.

**Key steps:**
1. Prepare BAM files for training samples and place them in `data/bam/`
2. Generate plan files for all samples (both training and query samples)
3. Invoke the `train_models` rule explicitly
4. The CNV calling workflow will use the newly trained models

**Example commands:**
```bash
cd Identify_gCNV_with_WES

# Step 1: Generate plans for all samples (training + query)
python scripts/agents/plan_agent.py --sample CTRL001 --bam ../data/bam/CTRL001.recal.bam --out ../plans/CTRL001.plan.yaml
python scripts/agents/plan_agent.py --sample CASE001 --bam ../data/bam/CASE001.recal.bam --out ../plans/CASE001.plan.yaml

# Step 2: Explicitly run the model training rule
snakemake --snakefile workflow/Snakefile -R train_models --cores 4

# Step 3: Now run the full CNV detection workflow
snakemake --snakefile workflow/Snakefile --cores 4
```

The full workflow includes annotation of the joint clustered VCF via AnnotSV and generation of visualization outputs such as knotAnnotSV and vcf2circos.

**Important notes:**
- Model training uses control samples to learn background read count variation
- The Snakemake workflow now implements the core training steps in `train_models` via `train_ploidy_model` and `train_baseline_model`
- `scripts/train_model.py` is a convenience wrapper that invokes the Snakemake training rule
- Training parameters (epochs, sample fraction) can be configured in `workflow/config.yaml` under `model_training:`
- Once models are trained and saved to `model/baseline-model` and `model/ploidy-model`, subsequent runs will use these trained models

### Plan Mode
Prioritizes per-sample plan files in `plans/`. Plan files specify sample name, BAM path, reference sequence, interval list, model path, GATK command, work directory, and other information.

### Direct BAM Mode
If no plan files exist in `plans/`, the Snakefile automatically scans `data/bam/*.bam` and generates default inputs based on sample names. This mode is suitable for quick tests or simple data structures, but plan files are recommended for explicit path and parameter management.

### Configuration File Description
Main configuration file: `Identify_gCNV_with_WES/workflow/config.yaml`

This file includes:
- Reference genome, dictionary, interval list, model paths
- Joint segmentation settings, including the filtered interval list and pedigree file
- Tool command names like GATK, BWA, samtools, Picard
- Visualization tools and annotation resource paths
- Model training parameters under `model_training:` section

`plan_agent.py` reads defaults from this file to generate plan files, facilitating consistent paths across different machines.

## Agents Usage Examples

- Generate a plan:
```bash
cd Identify_gCNV_with_WES
python scripts/agents/plan_agent.py --sample HG00099 --bam ../data/bam/HG00099.recal.bam --out ../plans/HG00099.plan.yaml
```

- Validate and print the run command:
```bash
cd Identify_gCNV_with_WES
python scripts/agents/run_agent.py --plan ../plans/HG00099.plan.yaml --cores 2
```

- Execute the plan directly:
```bash
cd Identify_gCNV_with_WES
python scripts/agents/run_agent.py --plan ../plans/HG00099.plan.yaml --cores 4 --execute
```

- Generate QC report:
```bash
cd Identify_gCNV_with_WES
python scripts/agents/qc_agent.py --plan ../plans/HG00099.plan.yaml --out ../outputs/HG00099.qc.yaml
```

- Package for publishing:
```bash
cd Identify_gCNV_with_WES
python scripts/agents/publish_agent.py --plan ../plans/HG00099.plan.yaml --out-dir ../outputs/publish/HG00099 --package
```

## Docker Usage

To use Docker, build the image in the `Identify_gCNV_with_WES/` directory:
```bash
cd Identify_gCNV_with_WES
docker build -t cnv-detection .
```

Recommended: Mount the entire repository and run inside the container:
```bash
docker run --rm -it \
  -v $(pwd):/workspace \
  -w /workspace/Identify_gCNV_with_WES \
  cnv-detection \
  bash -lc "snakemake --snakefile workflow/Snakefile --configfile workflow/config.yaml -n"
```

Mount only necessary directories:
```bash
docker run --rm -it \
  -v $(pwd)/Identify_gCNV_with_WES:/workspace \
  -v $(pwd)/data:/workspace/data \
  -v $(pwd)/plans:/workspace/plans \
  -v $(pwd)/outputs:/workspace/outputs \
  -w /workspace \
  cnv-detection \
  bash -lc "snakemake --snakefile workflow/Snakefile --configfile workflow/config.yaml --cores 4"
```

### Docker Tips
- Avoid packaging large data files into the image; mount `data/`, `plans/`, `outputs/` externally.
- Paths in `workflow/config.yaml` are typically relative, so use `Identify_gCNV_with_WES/` as the container working directory.

## Common Commands
- Create Conda environment: `make env-conda`
- Create local venv: `make env-venv`
- Run smoke tests: `make smoke`
- Snakemake dry-run: `make snakemake-dry`
- Build Docker image: `make docker-build`
- Run Docker: `make docker-run`

## Other Notes
- When using `plans/` mode, ensure that `bam` and `workpath` entries in the plan point to correct files or directories.
- Modify `Identify_gCNV_with_WES/workflow/config.yaml` according to your local environment for tool command names and resource paths.
- `Identify_gCNV_with_WES/scripts/agents/plan_agent.py` checks BAM file size and provides notes for small BAM files.

## License
This project is licensed under the MIT License.