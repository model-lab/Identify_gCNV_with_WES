#!/usr/bin/env python3
"""Visualize CNV summary: generate a PNG placeholder for smoke/testing.
If matplotlib is available, draw a simple bar summarizing counts.
"""
import argparse
import os
from utils import ensure_parent_dir, write_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in', dest='inp', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    try:
        import matplotlib.pyplot as plt
    except Exception:
        ensure_parent_dir(args.out)
        # create empty placeholder file
        write_text(args.out, '')
        print('matplotlib not available; wrote empty placeholder', args.out)
        return

    # simple placeholder figure
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.bar(['DEL', 'DUP'], [1, 0])
    ax.set_title('CNV summary (placeholder)')
    plt.tight_layout()
    ensure_parent_dir(args.out)
    fig.savefig(args.out)
    print('Wrote figure to', args.out)


if __name__ == '__main__':
    main()
