---
name: run-agent
description: |
  Agent to execute the CNV calling workflow for a single sample using a plan YAML produced by the `plan-agent`.
  Validates the plan and constructs a safe `snakemake` invocation. By default the agent prints the command
  and performs no destructive actions unless `--execute` is provided.
argument-hint: "--plan <path/to/plan.yaml> [--cores N] [--execute]"
---

Behavior and capabilities:
- Validates required keys in the plan YAML (`sample`, `bam`, `workpath`, `model`).
- Builds a `snakemake` command targeting the configured workflow and plan file.
- Optional `--execute` runs the command locally (requires `snakemake` available).

When to use:
- After generating a plan with `plan-agent`, use this agent to run the workflow reproducibly for that sample.

Example invocation:
```bash
python scripts/agents/run_agent.py --plan plans/HG0001.plan.yaml --cores 4 --execute
```

Notes:
- This agent does not upload results or modify archives; use the `publish-agent` for packaging and upload guidance.
