---
name: qc-agent
description: |
  Agent to perform lightweight quality checks on workflow outputs for a single sample.
  Reads a `plan.yaml` (or deduces `workpath` from the plan) and emits a small QC report (YAML/JSON)
  containing presence checks and simple file-size based heuristics.
argument-hint: "--plan <path/to/plan.yaml> [--out qc/HG0001.qc.yaml]"
---

Behavior and capabilities:
- Verifies expected output directory exists and lists key files.
- Reports missing outputs and simple heuristics (file size, file counts).
- Writes a machine-readable QC report and prints a human summary.

When to use:
- After running the workflow for a sample to quickly validate that outputs were produced and are non-empty.

Example invocation:
```bash
python scripts/agents/qc_agent.py --plan plans/HG0001.plan.yaml --out qc/HG0001.qc.yaml
```
