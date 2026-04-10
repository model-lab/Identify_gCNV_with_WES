#!/usr/bin/env python3
"""Run-agent: validate a plan and (optionally) execute snakemake for that plan."""
import argparse
import os
import sys
import yaml
import shlex
import subprocess


def load_plan(path):
    with open(path) as fh:
        return yaml.safe_load(fh)


def validate_plan(plan):
    required = ['sample', 'bam', 'workpath']
    missing = [k for k in required if k not in plan]
    return missing


def build_command(plan_path, snakemake_bin='snakemake', cores=1):
    cmd = [snakemake_bin, '--snakefile', 'workflow/Snakefile', '--configfile', plan_path, '--cores', str(cores)]
    return cmd


def main():
    parser = argparse.ArgumentParser(description='Run workflow for a plan')
    parser.add_argument('--plan', required=True)
    parser.add_argument('--cores', type=int, default=1)
    parser.add_argument('--execute', action='store_true', help='Run snakemake instead of printing the command')
    parser.add_argument('--snakemake-bin', default='snakemake')
    args = parser.parse_args()

    plan = load_plan(args.plan)
    missing = validate_plan(plan)
    if missing:
        print('Plan is missing required keys:', ', '.join(missing), file=sys.stderr)
        sys.exit(2)

    cmd = build_command(args.plan, snakemake_bin=args.snakemake_bin, cores=args.cores)
    print('Constructed command:')
    print(' '.join(shlex.quote(x) for x in cmd))

    if args.execute:
        print('Executing snakemake...')
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print('snakemake failed with return code', e.returncode, file=sys.stderr)
            sys.exit(e.returncode)


if __name__ == '__main__':
    main()
