#!/bin/bash

# Activate the conda environment
eval "$(conda shell.bash hook)"
conda activate gatk

# Define variables
reference="path_to_reference_genome (hg19_chr20.fa)"
interval="path_to_exon_interval (gc.filtered.500.interval_list)"
workpath="path_to_work_directory"
gatk="path_to_gatk"
java_para="-Xmx24g"
vcflist_path="path_to_vcf_files"
pedigree_file="path_to_pedigree_file (test_samples_pedigree.ped)"  # Path to the pedigree file of the samples in vcf list

# List of genotyped segments VCF files and perform Joint Germline CNV Segmentation
sample_vcf=$(ls ${vcflist_path}/*.genotyped-segments.vcf.gz | sed 's/ / -V /g')

if $gatk --java-options $java_para JointGermlineCNVSegmentation \
    -R ${reference} \
    -V ${sample_vcf} \
    --model-call-intervals ${interval} \
    --pedigree ${pedigree_file} \
    -O ${workpath}/cnv_gvcf_clustered.vcf.gz;then
    echo "Step completed: JointGermlineCNVSegmentation"
else
    echo "Error in step: JointGermlineCNVSegmentation" >&2
    exit 1
fi