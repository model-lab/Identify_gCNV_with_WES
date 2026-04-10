# Identify_gCNV_with_WES
Analysis workflow to assess germline copy number variants from human whole-exome sequencing
## Quick start

1. Install dependencies (conda recommended):

```bash
conda env create -f environment.yml
conda activate cnv_workflow
```

2. (Optional) Install Git LFS for large genome files:

```bash
git lfs install
```

3. Generate a per-sample plan (or let Snakemake run the plan agent rule):

```bash
# example: generate plan for sample 'HG00099'
python scripts/plan_agent.py --sample HG00099 --bam data/bam/HG00099.recal.bam --out plans/HG00099.plan.yaml
```

4. Run Snakemake from the `snakemake` directory to execute the pipeline for a sample (or customize `Snakefile` targets):

```bash
cd snakemake
snakemake --cores 4 run_plan_agent output: ../plans/HG00099.plan.yaml
snakemake --cores 4 collect_read_counts
```

See `config.yaml` for configurable paths (references, models, workdir).
