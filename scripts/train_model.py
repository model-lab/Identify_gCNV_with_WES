#!/usr/bin/env python3
"""Train-model wrapper: invoke the Snakemake train_models rule."""
import argparse
import os
import subprocess


def main():
    parser = argparse.ArgumentParser(description='Run the Snakemake train_models rule')
    parser.add_argument('--cores', type=int, default=1, help='Number of cores for Snakemake')
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    cmd = [
        'snakemake',
        '--snakefile', os.path.join(repo_root, 'workflow', 'Snakefile'),
        '-R', 'train_models',
        '--cores', str(args.cores),
    ]
    print('Running:', ' '.join(cmd))
    subprocess.check_call(cmd, cwd=repo_root)


if __name__ == '__main__':
    main()
