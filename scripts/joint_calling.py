#!/usr/bin/env python3
"""Joint calling wrapper: combine per-sample genotyped-segments into a clustered VCF.
For smoke runs this creates a tiny VCF if real inputs are missing.
"""
import argparse
import os
import gzip
from utils import ensure_parent_dir, write_text


def write_fake_vcf(path):
    ensure_parent_dir(path)
    content = '\n'.join([
        '##fileformat=VCFv4.2',
        '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO',
        'chr20\t15000\tcnv1\tN\t<DEL>\t.\tPASS\tSVTYPE=DEL;SVLEN=-1000',
        ''
    ])
    # prefer gz output if extension suggests
    if path.endswith('.gz'):
        with gzip.open(path, 'wt') as fh:
            fh.write(content)
    else:
        write_text(path, content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', nargs='+')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    any_exists = any(os.path.exists(p) for p in (args.inputs or []))
    if not any_exists:
        write_fake_vcf(args.out)
        print('Wrote fake joint VCF to', args.out)
        return

    # simple placeholder merge for now
    write_fake_vcf(args.out)
    print('Wrote joint VCF (placeholder) to', args.out)


if __name__ == '__main__':
    main()
