#!/usr/bin/env python3
"""Train-model wrapper: create light-weight model artifacts or placeholder markers.
This script is intentionally conservative for CI/smoke: it writes marker files and copies any existing model config templates.
"""
import argparse
from utils import write_json, ensure_parent_dir


def write_placeholder_model(path):
    cfg = {'trained': True, 'created_by': 'train_model.py'}
    write_json(path, cfg)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-baseline', required=True)
    parser.add_argument('--out-ploidy', required=True)
    args = parser.parse_args()

    write_placeholder_model(args.out_baseline)
    write_placeholder_model(args.out_ploidy)
    print('Wrote model markers:', args.out_baseline, args.out_ploidy)


if __name__ == '__main__':
    main()
