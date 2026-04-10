#!/usr/bin/env python3
"""QC-agent: produce a small QC report for a sample based on a plan."""
import argparse
import os
import sys
import yaml
import time


def load_plan(path):
    with open(path) as fh:
        return yaml.safe_load(fh)


def collect_basic_qc(workpath, sample):
    report = {'sample': sample, 'workpath': workpath, 'timestamp': time.asctime(), 'files': [], 'summary': {}}
    if not os.path.exists(workpath):
        report['summary']['status'] = 'missing_workpath'
        return report

    total_size = 0
    count = 0
    for root, dirs, files in os.walk(workpath):
        for fn in files:
            path = os.path.join(root, fn)
            try:
                size = os.path.getsize(path)
            except Exception:
                size = None
            report['files'].append({'path': path, 'size': size})
            if size:
                total_size += size
            count += 1

    report['summary']['file_count'] = count
    report['summary']['total_size_bytes'] = total_size
    report['summary']['status'] = 'ok' if count > 0 else 'empty'
    return report


def main():
    parser = argparse.ArgumentParser(description='Generate QC report from plan')
    parser.add_argument('--plan', required=True)
    parser.add_argument('--out', help='Output QC YAML path (default: prints to stdout)')
    args = parser.parse_args()

    plan = load_plan(args.plan)
    sample = plan.get('sample', 'UNKNOWN')
    workpath = plan.get('workpath', os.path.join('work', sample))
    # fallback to outputs/<sample> when smoke tests or simple runs place outputs there
    if not os.path.exists(workpath):
        alt = os.path.join('outputs', sample)
        if os.path.exists(alt):
            workpath = alt

    report = collect_basic_qc(workpath, sample)

    if args.out:
        outdir = os.path.dirname(args.out)
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)
        with open(args.out, 'w') as fh:
            yaml.safe_dump(report, fh, sort_keys=False)
        print('QC written to', args.out)
    else:
        yaml.safe_dump(report, sys.stdout, sort_keys=False)


if __name__ == '__main__':
    main()
