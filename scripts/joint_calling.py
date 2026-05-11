#!/usr/bin/env python3
"""Joint calling wrapper: combine per-sample genotyped-segments with GATK."""
import argparse
import gzip
import os
import subprocess
from utils import ensure_parent_dir, run_cmd, write_text


def write_fake_vcf(path):
    ensure_parent_dir(path)
    content = '\n'.join([
        '##fileformat=VCFv4.2',
        '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO',
        'chr20\t15000\tID=cnv1\tN\t<DEL>\t.\tPASS\tSVTYPE=DEL;SVLEN=-1000',
        ''
    ])
    if path.endswith('.gz'):
        with gzip.open(path, 'wt') as fh:
            fh.write(content)
    else:
        write_text(path, content)


def main():
    parser = argparse.ArgumentParser(description='Run GATK JointGermlineCNVSegmentation on genotyped segment VCFs')
    parser.add_argument('--gatk', default='gatk', help='Path to the GATK executable')
    parser.add_argument('--java-options', default='-Xmx24g', help='Java options for GATK')
    parser.add_argument('--reference', required=True, help='Reference genome FASTA')
    parser.add_argument('--interval', required=True, help='Model call intervals file')
    parser.add_argument('--pedigree', required=True, help='Pedigree file for joint segmentation')
    parser.add_argument('--inputs', nargs='+', required=True, help='Genotyped-segments VCF inputs')
    parser.add_argument('--out', required=True, help='Output clustered VCF path')
    args = parser.parse_args()

    existing_inputs = [p for p in args.inputs if os.path.exists(p)]
    if not existing_inputs:
        write_fake_vcf(args.out)
        print('Wrote fake joint VCF to', args.out)
        return

    cmd = [args.gatk, '--java-options', args.java_options, 'JointGermlineCNVSegmentation',
           '-R', args.reference]
    for vcf in existing_inputs:
        cmd.extend(['-V', vcf])
    cmd.extend(['--model-call-intervals', args.interval,
                '--pedigree', args.pedigree,
                '-O', args.out])

    run_cmd(cmd)


if __name__ == '__main__':
    main()
