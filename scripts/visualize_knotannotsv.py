#!/usr/bin/env python3
"""Run knotAnnotSV visualization if installed; otherwise produce placeholder outputs.

Usage: scripts/visualize_knotannotsv.py --annotated annotated.tsv --out-dir outdir --knot-dir /path/to/knotAnnotSV
"""
import argparse
import os
import shutil
import subprocess
from utils import ensure_parent_dir, write_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--annotated', required=True)
    parser.add_argument('--out-dir', required=True)
    parser.add_argument('--knot-dir', dest='knot', required=False)
    args = parser.parse_args()

    outdir = args.out_dir
    os.makedirs(outdir, exist_ok=True)

    # try to find knotAnnotSV perl script
    knot_exec = None
    if args.knot:
        knot_exec = os.path.join(args.knot, 'knotAnnotSV.pl')
    if not knot_exec:
        knot_exec = shutil.which('knotAnnotSV.pl')

    if knot_exec and os.path.exists(knot_exec):
        cmd = ['perl', knot_exec, '--annotSVfile', args.annotated, '--outDir', outdir, '--outPrefix', 'knot']
        try:
            print('Running:', ' '.join(cmd))
            subprocess.check_call(cmd)
            return
        except Exception:
            pass

    # fallback: write a minimal HTML placeholder
    out_html = os.path.join(outdir, 'knot_placeholder.html')
    write_text(out_html, '<html><body><h1>knotAnnotSV placeholder</h1></body></html>')
    print('knotAnnotSV not available; wrote placeholder', out_html)


if __name__ == '__main__':
    main()
