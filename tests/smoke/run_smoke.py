#!/usr/bin/env python3
"""Simple smoke-run harness: run key scripts with placeholder inputs to verify behavior.
"""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / 'tests' / 'smoke' / 'tmp'


def run(cmd):
    print('CMD:', ' '.join(cmd))
    subprocess.check_call(cmd)


def main():
    TMP.mkdir(parents=True, exist_ok=True)

    # create a tiny fake BAM to reference in the sample plan
    fake_bam = TMP / 'EXAMPLE.recal.bam'
    fake_bam.parent.mkdir(parents=True, exist_ok=True)
    fake_bam.write_bytes(b'')

    # write a simple plan yaml to exercise plan-based paths
    plan_path = ROOT / 'plans' / 'EXAMPLE.plan.yaml'
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_content = '\n'.join([
        'sample: EXAMPLE',
        f"bam: {str(fake_bam)}",
        'reference: data/hg19_chr20.fa.gz',
        'workpath: outputs/EXAMPLE',
    ]) + '\n'
    plan_path.write_text(plan_content)

    # 1. preprocess_intervals -> write to TMP
    out_interval = TMP / 'targets.preprocessed.500.interval_list'
    run(['python3', str(ROOT / 'scripts' / 'preprocess_intervals.py'), '--out', str(out_interval)])

    # 2. train_model (placeholders)
    out_base = TMP / 'baseline.trained.json'
    out_ploidy = TMP / 'ploidy.trained.json'
    run(['python3', str(ROOT / 'scripts' / 'train_model.py'), '--out-baseline', str(out_base), '--out-ploidy', str(out_ploidy)])

    # 3. joint_calling -> creates gz VCF placeholder (no inputs provided)
    out_vcf = TMP / 'cnv_gvcf_clustered.vcf.gz'
    run(['python3', str(ROOT / 'scripts' / 'joint_calling.py'), '--out', str(out_vcf)])

    # 4. AnnotSV annotation (wrapper)
    out_tsv = TMP / 'cnv_gvcf_clustered.annotated.tsv'
    run(['python3', str(ROOT / 'scripts' / 'run_annotsv.py'), '--in', str(out_vcf), '--out', str(out_tsv), '--annotations-dir', str(ROOT / 'data' / 'AnnotSV_annotations')])

    # 5a. knotAnnotSV visualization wrapper
    knot_out = TMP / 'knot_out'
    run(['python3', str(ROOT / 'scripts' / 'visualize_knotannotsv.py'), '--annotated', str(out_tsv), '--out-dir', str(knot_out)])

    # 5b. vcf2circos visualization wrapper
    vcf2_out = TMP / 'vcf2_out'
    run(['python3', str(ROOT / 'scripts' / 'visualize_vcf2circos.py'), '--vcf', str(out_vcf), '--out-dir', str(vcf2_out)])

    # 6. basic CNV visualization (matplotlib placeholder)
    fig_out = TMP / 'cnv_summary.png'
    run(['python3', str(ROOT / 'scripts' / 'visualize_cnv.py'), '--in', str(out_tsv), '--out', str(fig_out)])

    print('\nSmoke outputs:')
    outputs = [out_interval, out_base, out_ploidy, out_vcf, out_tsv, knot_out, vcf2_out]
    for p in outputs:
        if p.exists():
            size = p.stat().st_size
        else:
            # if directory, report contents
            if p.is_dir():
                items = list(p.iterdir())
                size = sum(i.stat().st_size for i in items if i.exists()) if items else 0
            else:
                size = '-'
        print(p, '->', 'exists' if p.exists() else 'MISSING', 'size', size)


if __name__ == '__main__':
    main()
