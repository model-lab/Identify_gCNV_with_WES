#!/bin/bash

# Script to download annotation files and datasets from Zenodo

# Define Zenodo URLs and output paths
zenodo_base_url="https://zenodo.org/record/19489460/files"
files=(
  "UCSC_RefGene_hg19.bed.gz"
  "contig_ploidy_priors.tsv"
  "gc.filtered.500.interval_list"
  "hg19_chr20.dict"
  "hg19_chr20.fa.gz"
  "hg19_chr20.fa.gz.fai"
  "hg19_chr20.fa.gz.gzi"
  "hg19_chr20.interval_list"
  "targets.preprocessed.500.annotated_intervals.tsv"
  "targets.preprocessed.500.interval_list"
  "test_samples_pedigree.ped"
)

# Create output directory
output_dir="data/"
mkdir -p $output_dir

# Download each file
for file in "${files[@]}"; do
  wget -O "$output_dir/$file" "$zenodo_base_url/$file"
done

echo "All files downloaded to $output_dir."