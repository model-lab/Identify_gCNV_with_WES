**Agents Overview**

- **Plan Agent**: produces a per-sample YAML plan consumed by the workflow. See `agents/plan.agent.md` and `scripts/plan_agent.py`.
- **Run Agent**: validates a plan and constructs (optionally runs) a `snakemake` invocation. See `agents/run.agent.md` and `scripts/agents/run_agent.py`.
- **QC Agent**: inspects the sample `workpath` and emits a small QC report. See `agents/qc.agent.md` and `scripts/agents/qc_agent.py`.
- **Publish Agent**: packages results into a folder/tarball and writes minimal metadata for manual upload. See `agents/publish.agent.md` and `scripts/agents/publish_agent.py`.

Usage patterns
- Generate a plan: `python scripts/plan_agent.py --sample <S> --bam <BAM> --out plans/<S>.plan.yaml`
- Run workflow (dry-run): `python scripts/agents/run_agent.py --plan plans/<S>.plan.yaml`
- Run workflow (execute): `python scripts/agents/run_agent.py --plan plans/<S>.plan.yaml --execute --cores 4`
- QC: `python scripts/agents/qc_agent.py --plan plans/<S>.plan.yaml --out qc/<S>.qc.yaml`
- Package: `python scripts/agents/publish_agent.py --plan plans/<S>.plan.yaml --out-dir publish/<S> --package`

Security & Safety
- Agents are intentionally conservative: `run-agent` prints the `snakemake` command by default and only executes when `--execute` is provided.
- `publish-agent` does not upload artifacts automatically to remote services — uploading requires separate CI steps with credentials or manual user action.
- Review generated `METADATA.yaml` before publishing; ensure no sensitive data (personal identifiers) are included.

Extending agents
- Add new agents under `agents/` (descriptor) and `scripts/agents/` (implementation). Follow existing examples for frontmatter and argument-hint.
