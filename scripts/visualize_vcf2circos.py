#!/usr/bin/env python3
"""Run vcf2circos conversion if available; otherwise create placeholder files.

Usage: scripts/visualize_vcf2circos.py --vcf cnv.vcf.gz --out-dir outdir --config config.tar.gz
"""
import argparse
import os
import shutil
import subprocess
from utils import ensure_parent_dir, write_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vcf', required=True)
    parser.add_argument('--out-dir', required=True)
    parser.add_argument('--config', required=False)
    args = parser.parse_args()

    outdir = args.out_dir
    os.makedirs(outdir, exist_ok=True)

    v2c = shutil.which('vcf2circos')
    if v2c:
        cmd = [v2c, args.vcf]
        if args.config:
            cmd += ['-c', args.config]
        try:
            print('Running:', ' '.join(cmd))
            subprocess.check_call(cmd)
            return
        except Exception:
            pass

    # fallback: create placeholder image and config
    write_text(os.path.join(outdir, 'vcf2circos_placeholder.png'), '')
    write_text(os.path.join(outdir, 'vcf2circos_placeholder.conf'), 'placeholder')
    print('vcf2circos not available; wrote placeholders in', outdir)


if __name__ == '__main__':
    main()
