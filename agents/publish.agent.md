---
name: publish-agent
description: |
  Agent to package and prepare sample results for sharing (e.g., Zenodo). The agent collects key
  deliverables from the sample `workpath`, builds a reproducible archive (tar.gz) and a metadata
  README suitable for upload. It does NOT upload automatically — upload must be done by the user
  or a separate CI step with credentials.
argument-hint: "--plan <path/to/plan.yaml> --out-dir publish/HG0001 --package"
---

Behavior and capabilities:
- Collects candidate result files (VCF, denoised ratios, genotyped segments) into an output folder.
- Generates a minimal `METADATA.yaml` describing the sample, workflow commit, and included files.
- Optionally creates a compressed `tar.gz` for manual upload.

When to use:
- After verifying QC, use this agent to prepare an upload package for Zenodo or institutional repositories.

Example invocation:
```bash
python scripts/agents/publish_agent.py --plan plans/HG0001.plan.yaml --out-dir publish/HG0001 --package
```
