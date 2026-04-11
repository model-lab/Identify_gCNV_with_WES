#!/usr/bin/env python3
"""Annotate CNV calls: create a small TSV summary from a joint VCF for downstream review.
"""
import argparse
import os
import gzip
from utils import ensure_parent_dir, write_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in', dest='inp', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    if not os.path.exists(args.inp):
        print('Input not found:', args.inp)
        return

    ensure_parent_dir(args.out)
    lines = ['chrom\tstart\tend\ttype\tnotes']
    # support gzipped or plain VCF-like input
    open_fn = gzip.open if args.inp.endswith('.gz') else open
    with open_fn(args.inp, 'rt', encoding='utf-8', errors='replace') as fh_in:
        for line in fh_in:
            if line.startswith('#'):
                continue
            cols = line.strip().split('\t')
            if len(cols) < 2:
                continue
            chrom = cols[0]
            pos = cols[1]
            info = cols[7] if len(cols) > 7 else ''
            try:
                end = int(pos) + 1000
            except Exception:
                end = ''
            lines.append(f"{chrom}\t{pos}\t{end}\tDEL\t{info}")

    write_text(args.out, '\n'.join(lines) + '\n')
    print('Wrote annotation TSV to', args.out)


if __name__ == '__main__':
    main()
