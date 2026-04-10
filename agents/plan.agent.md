---
name: plan-agent
description: |
  An automation agent that inspects a sample's BAM and repository context to generate a per-sample CNV analysis plan for the Snakemake workflow. The plan contains file paths (reference, interval list), model choices, and runtime parameters. The agent is intended to be run as a Snakemake step (`run_plan_agent`) which produces a YAML plan consumed by downstream rules or by humans reviewing the planned parameters.
argument-hint: "--sample <sample_name> --bam <path/to.bam> --out <path/to/plan.yaml>"
---

Behavior and capabilities:
- Reads sample metadata and basic file characteristics to suggest suitable parameters (model paths, interval lists, work directory).
- Emits a YAML plan file with keys: `reference`, `reference_dict`, `interval`, `model`, `ploidy_model`, `workpath`, `gatk`, `notes`.
- Designed to be deterministic and safe; does not modify input data.

When to use:
- Run this agent before CNV calling to generate reproducible, reviewable parameters for each sample.

Example invocation:
```bash
python scripts/plan_agent.py --sample HG0001 --bam data/bam/HG0001.recal.bam --out plans/HG0001.plan.yaml
```

Notes:
- This file is a human-readable description of the agent and how it should be used. The actual logic is implemented in `scripts/plan_agent.py`.
