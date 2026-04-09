#!/bin/bash

# Activate the conda environment for AnnotSV
eval "$(conda shell.bash hook)"
conda activate annotsv

# Define variables
AnnotSV_annotations="path_to_annotation_file_directory"
vcf="path_to_vcf_file"  # Specify the path to your VCF file
workpath="path_to_output_directory"  # Specify the output directory
output_file="output_file_name" # Specify the output file

# Run AnnotSV

if AnnotSV -annotationsDir "${AnnotSV_annotations}" \
    -SVinputFile "${vcf}" \
    -outputFile "${output_file}"; then
    echo "Step completed: AnnotSV"
else
    echo "Error in step: AnnotSV" >&2
    exit 1
fi
