#!/usr/bin/env python3
"""Preprocess a BED-like targets file into an interval_list used by the workflow.
Uses `scripts/utils.py` helpers and provides clear logging and safe directory creation.
"""
import argparse
import os
from utils import ensure_parent_dir, write_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in', dest='inp')
    parser.add_argument('--out', dest='out', required=True)
    args = parser.parse_args()

    ensure_parent_dir(args.out)

    if args.inp and os.path.exists(args.inp):
        lines = []
        with open(args.inp) as fh:
            for line in fh:
                if line.strip() and not line.startswith('#'):
                    fields = line.strip().split()[:3]
                    lines.append('\t'.join(fields))
        write_text(args.out, '\n'.join(lines) + '\n')
    else:
        # create tiny example interval
        write_text(args.out, 'chr20\t10000\t20000\n')
    print('Wrote intervals to', args.out)


if __name__ == '__main__':
    main()
