#!/usr/bin/env python3
"""
Simple plan agent for CNV workflow.
Generates a YAML plan with paths and parameters for a given sample.
This is a lightweight placeholder for an LLM/agent integration point.
"""
import argparse
import os
import sys
import yaml


def guess_params(sample, bam, out, config_path=None):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # sensible defaults within the repository; allow override from workflow/config.yaml
    if config_path is None:
        config_path = os.path.join(repo_root, 'workflow', 'config.yaml')
    reference = os.path.join(repo_root, 'data', 'hg19_chr20.fa.gz')
    reference_dict = os.path.join(repo_root, 'data', 'hg19_chr20.dict')
    interval = os.path.join(repo_root, 'data', 'targets.preprocessed.500.interval_list')
    model = os.path.join(repo_root, 'model', 'baseline-model')
    ploidy_model = os.path.join(repo_root, 'model', 'ploidy-model')
    gatk = 'gatk'
    workpath = os.path.join(repo_root, 'work', sample)

    # Load config.yaml if present to override defaults
    cfg = {}
    try:
        if os.path.exists(config_path):
            with open(config_path) as cf:
                cfg = yaml.safe_load(cf) or {}
            # resolve repo-relative paths
            def _rpath(v):
                if not v:
                    return v
                return v if os.path.isabs(v) else os.path.join(repo_root, v)

            reference = _rpath(cfg.get('reference', reference))
            reference_dict = _rpath(cfg.get('reference_dict', reference_dict))
            interval = _rpath(cfg.get('interval', interval))
            model = _rpath(cfg.get('model', model))
            ploidy_model = _rpath(cfg.get('ploidy_model', ploidy_model))
            gatk = cfg.get('gatk', gatk)
            workpath = _rpath(cfg.get('workdir', workpath))
    except Exception:
        pass

    notes = []
    if not os.path.exists(bam):
        notes.append(f"BAM not found at {bam}; ensure preprocessing completed.")
    else:
        try:
            size = os.path.getsize(bam)
            if size < 50_000_000:
                notes.append('Detected small BAM (<50MB): consider lower sensitivity settings or check coverage.')
        except Exception:
            pass

    plan = {
        'sample': sample,
        'bam': os.path.abspath(bam),
        'reference': reference,
        'reference_dict': reference_dict,
        'interval': interval,
        'model': model,
        'ploidy_model': ploidy_model,
        'gatk': gatk,
        'bwa': cfg.get('bwa', 'bwa'),
        'samtools': cfg.get('samtools', 'samtools'),
        'picard': cfg.get('picard', 'picard'),
        'annotsv': cfg.get('annotsv', 'annotsv'),
        'plotcnv_Rscript': cfg.get('plotcnv_Rscript', 'Rscript'),
        'handycnv_Rscript': cfg.get('handycnv_Rscript', 'Rscript'),
        'igv': cfg.get('igv', 'igv'),
        'segmentmodel_spy_url': cfg.get('segmentmodel_spy_url'),
        'workpath': workpath,
        'notes': notes,
    }
    return plan


def main():
    parser = argparse.ArgumentParser(description='Generate a CNV analysis plan for a sample')
    parser.add_argument('--sample', required=True)
    parser.add_argument('--bam', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--config', required=False, help='Optional workflow config.yaml to read defaults from')
    args = parser.parse_args()

    plan = guess_params(args.sample, args.bam, args.out, config_path=args.config)

    outdir = os.path.dirname(args.out)
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    with open(args.out, 'w') as fh:
        yaml.safe_dump(plan, fh, sort_keys=False)

    print(f"Plan written to {args.out}")


if __name__ == '__main__':
    main()
