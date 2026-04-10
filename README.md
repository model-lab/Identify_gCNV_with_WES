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

4. Run Snakemake from the `workflow/` directory to execute the pipeline for a sample (or customize `Snakefile` targets):

```bash
cd workflow
snakemake --cores 4 run_plan_agent --configfile config.yaml
snakemake --cores 4 collect_read_counts --configfile config.yaml
```

See `workflow/config.yaml` for configurable paths (references, models, workdir).

Project layout (standardized):

- `workflow/` : Snakemake `Snakefile`, `config.yaml`, and smoke tests
- `scripts/`  : helper scripts (plan agent, download, etc.)
- `data/`     : reference fasta, interval lists, prepared inputs
- `model/`    : trained models used by callers
- `plans/`    : per-sample plan yaml files
- `outputs/`  : generated results (suggested output dir)

If you want to keep the old `snakemake/` folder as a backup, it's safe to do so, otherwise you can remove it after verifying `workflow/` runs correctly.

Agents (examples)
- Generate a plan for a sample:

```bash
python scripts/plan_agent.py --sample HG00099 --bam data/bam/HG00099.recal.bam --out plans/HG00099.plan.yaml
```

- Dry-run the run-agent (prints `snakemake` command):

```bash
python scripts/agents/run_agent.py --plan plans/HG00099.plan.yaml --cores 2
```

- Run QC on a plan's outputs:

```bash
python scripts/agents/qc_agent.py --plan plans/HG00099.plan.yaml --out qc/HG00099.qc.yaml
```

- Prepare a publish package (creates `publish/HG00099` and a tarball):

```bash
python scripts/agents/publish_agent.py --plan plans/HG00099.plan.yaml --out-dir publish/HG00099 --package
```
