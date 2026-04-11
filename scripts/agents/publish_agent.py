#!/usr/bin/env python3
"""Publish-agent: collect key outputs and prepare a package for manual upload."""
import argparse
import os
import sys
import yaml
import shutil
import tarfile
from pathlib import Path


def load_plan(path):
    with open(path) as fh:
        return yaml.safe_load(fh)


def gather_files(workpath):
    patterns = ['*.vcf.gz', '*.vcf', '*.tsv', '*.denoised-copy-ratios*', '*genotyped-segments*', '*.png', '*.html', '*.pdf', '*.xlsm']
    found = []
    p = Path(workpath)
    if not p.exists():
        return found
    for pat in patterns:
        for f in p.rglob(pat):
            found.append(str(f))
    return sorted(set(found))


def make_metadata(plan, files, outdir):
    meta = {'sample': plan.get('sample'), 'plan': plan, 'files': files}
    with open(os.path.join(outdir, 'METADATA.yaml'), 'w') as fh:
        yaml.safe_dump(meta, fh, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(description='Prepare package for publishing')
    parser.add_argument('--plan', required=True)
    parser.add_argument('--out-dir', required=True)
    parser.add_argument('--package', action='store_true', help='Create tar.gz package')
    args = parser.parse_args()

    plan = load_plan(args.plan)
    workpath = plan.get('workpath', os.path.join('work', plan.get('sample', 'UNKNOWN')))
    # fallback to outputs/<sample> for smoke runs
    if not os.path.exists(workpath):
        alt = os.path.join('outputs', plan.get('sample', 'UNKNOWN'))
        if os.path.exists(alt):
            workpath = alt

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir, exist_ok=True)

    files = gather_files(workpath)
    for f in files:
        dest = os.path.join(args.out_dir, os.path.relpath(f, workpath))
        ddir = os.path.dirname(dest)
        if ddir and not os.path.exists(ddir):
            os.makedirs(ddir, exist_ok=True)
        try:
            shutil.copy2(f, dest)
        except Exception:
            pass

    make_metadata(plan, files, args.out_dir)

    if args.package:
        tarpath = args.out_dir.rstrip('/') + '.tar.gz'
        with tarfile.open(tarpath, 'w:gz') as tar:
            tar.add(args.out_dir, arcname=os.path.basename(args.out_dir))
        print('Package created at', tarpath)
    else:
        print('Prepared publish folder at', args.out_dir)


if __name__ == '__main__':
    main()
