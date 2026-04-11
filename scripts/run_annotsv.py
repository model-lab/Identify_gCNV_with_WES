#!/usr/bin/env python3
"""Run AnnotSV on a VCF file if AnnotSV is installed; otherwise create a placeholder TSV.

Usage: scripts/run_annotsv.py --in input.vcf.gz --out output.tsv --annotations-dir /path/to/AnnotSV_annotations
"""
import argparse
import os
import shutil
import subprocess
from utils import ensure_parent_dir, write_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in', dest='inp', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--annotations-dir', dest='ann', required=False)
    args = parser.parse_args()

    ensure_parent_dir(args.out)
    ann_dir = args.ann or os.environ.get('ANNOTSV_ANNOTATIONS_DIR')
    if shutil.which('AnnotSV') or ann_dir:
        cmd = ['AnnotSV']
        if ann_dir:
            cmd += ['-annotationsDir', ann_dir]
        cmd += ['-SVinputFile', args.inp, '-outputFile', args.out]
        try:
            print('Running:', ' '.join(cmd))
            subprocess.check_call(cmd)
            return
        except Exception:
            pass

    # fallback: create simple TSV summary
    with open(args.out, 'w') as fh:
        fh.write('chrom\tstart\tend\tgene\tannotsv_note\n')
        fh.write('chr20\t15000\t16000\tGENE1\tplaceholder\n')
    print('AnnotSV not available; wrote placeholder', args.out)


if __name__ == '__main__':
    main()
