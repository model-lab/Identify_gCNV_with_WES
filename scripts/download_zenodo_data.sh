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

zenodo_v2_base_url="https://zenodo.org/record/22047704/files"
v2_files=(
  "EXAMPLE.bam"
  "EXAMPLE.bam.bai"
)

# Create output directory
output_dir="data/"
mkdir -p "$output_dir" || { echo "Error: Failed to create directory $output_dir"; exit 1; }

# Determine downloader tool (wget or curl)
if command -v wget >/dev/null 2>&1; then
  downloader="wget"
elif command -v curl >/dev/null 2>&1; then
  downloader="curl"
else
  echo "Error: Neither 'wget' nor 'curl' is installed. Please install one to proceed." >&2
  exit 1
fi

echo "Using $downloader for downloads..."

# Track failures
failed_downloads=0

# Download each file
for file in "${files[@]}"; do
  echo "Downloading $file..."
  
  if [ "$downloader" = "wget" ]; then
    # --show-progress keeps a clean progress bar
    wget --show-progress -O "$output_dir/$file" "$zenodo_base_url/$file"
  else
    # -f makes curl fail on HTTP errors (like 404); -L follows redirects
    curl -f -L -o "$output_dir/$file" "$zenodo_base_url/$file"
  fi

  # Check the exit status of the downloader tool
  if [ $? -ne 0 ]; then
    echo "Error: Failed to download $file" >&2
    failed_downloads=$((failed_downloads + 1))
  fi
done

for file in "${v2_files[@]}"; do
  echo "Downloading $file..."
  
  if [ "$downloader" = "wget" ]; then
    # --show-progress keeps a clean progress bar
    wget --show-progress -O "$output_dir/bam/$file" "$zenodo_v2_base_url/$file"
  else
    # -f makes curl fail on HTTP errors (like 404); -L follows redirects
    curl -f -L -o "$output_dir/bam/$file" "$zenodo_v2_base_url/$file"
  fi

  # Check the exit status of the downloader tool
  if [ $? -ne 0 ]; then
    echo "Error: Failed to download $file" >&2
    failed_downloads=$((failed_downloads + 1))
  fi
done

# Final status check
if [ "$failed_downloads" -gt 0 ]; then
  echo "Download complete with errors. $failed_downloads file(s) failed to download." >&2
  exit 1
else
  echo "All files successfully downloaded to $output_dir."
  exit 0
fi
