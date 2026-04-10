#!/bin/bash

# Activate the conda environment
eval "$(conda shell.bash hook)"
conda activate gatk

# Define variables
reference="path_to_reference_genome (hg19_chr20.fa)"
interval="path_to_exon_interval (hg19_chr20.interval_list)"
workpath="path_to_work_directory" # Same to cnv_calling.sh setting
gatk="path_to_gatk"
java_para="-Xmx24g"
bamlist_path="path_to_bam_files" # Using to train model

# Function to check and run a command if the output file does not exist
run_if_not_exists() {
    local output_file=$1
    shift
    local cmd=$@
    if [ ! -f $output_file ]; then
        echo "Running: $cmd"
        eval $cmd
        if [ $? -eq 0 ]; then
            echo "Step completed: $(basename $output_file)"
        else
            echo "Error in step: $(basename $output_file)" >&2
            exit 1
        fi
    else
        echo "File $output_file already exists. Skipping."
    fi
}

# Create CNV interval if it does not exist
run_if_not_exists ${workpath}/targets.preprocessed.500.interval_list \
    "$gatk --java-options $java_para PreprocessIntervals -R $reference -L $interval --bin-length 0 --padding 250 -imr OVERLAPPING_ONLY -O ${workpath}/targets.preprocessed.500.interval_list"

# Annotate intervals if it does not exist
run_if_not_exists ${workpath}/targets.preprocessed.500.annotated_intervals.tsv \
    "$gatk --java-options $java_para AnnotateIntervals -L ${workpath}/targets.preprocessed.500.interval_list -R $reference -imr OVERLAPPING_ONLY -O ${workpath}/targets.preprocessed.500.annotated_intervals.tsv"

# Collect read counts for each BAM file
for sample in ${bamlist_path}/*.bam; do
    filename=$(basename $sample .bam)
    run_if_not_exists ${workpath}/${filename}.readcounts.tsv \
        "$gatk --java-options $java_para CollectReadCounts -L ${workpath}/targets.preprocessed.500.interval_list -R $reference -imr OVERLAPPING_ONLY -I $sample --format TSV -O ${workpath}/${filename}.readcounts.tsv"
done
echo "Step completed: CollectReadCounts"


# Create a list of read count files
sample_rc=""
for file in ${workpath}/*readcounts.tsv; do
    sample_rc="${sample_rc} -I ${file}"
done

# Filter intervals if it does not exist
run_if_not_exists ${workpath}/gc.filtered.500.interval_list \
    "$gatk --java-options $java_para FilterIntervals -L ${workpath}/targets.preprocessed.500.interval_list --annotated-intervals ${workpath}/targets.preprocessed.500.annotated_intervals.tsv $sample_rc -imr OVERLAPPING_ONLY -O ${workpath}/gc.filtered.500.interval_list"

# Generate contig ploidy priors if it does not exist
run_if_not_exists ${workpath}/contig_ploidy_priors.tsv \
    "grep -v '^@' ${workpath}/targets.preprocessed.500.interval_list | awk -F\"\t\" '{print \$1}' | uniq | awk 'BEGIN {print \"CONTIG_NAME\tPLOIDY_PRIOR_0\tPLOIDY_PRIOR_1\tPLOIDY_PRIOR_2\tPLOIDY_PRIOR_3\"} {print \$1, 0.1, 0.3, 0.5, 0.1}' OFS=\"\t\" > ${workpath}/contig_ploidy_priors.tsv"

# Determine germline contig ploidy
if $gatk --java-options $java_para DetermineGermlineContigPloidy \
    -L ${workpath}/gc.filtered.500.interval_list \
    --interval-merging-rule OVERLAPPING_ONLY \
    $sample_rc \
    --contig-ploidy-priors ${workpath}/contig_ploidy_priors.tsv \
    --output ${workpath}/model \
    --output-prefix ploidy \
    --verbosity DEBUG;then
    echo "Step completed: DetermineGermlineContigPloidy"
else
    echo "Error in step: DetermineGermlineContigPloidy" >&2
    exit 1
fi

# Call germline CNVs
if $gatk --java-options $java_para GermlineCNVCaller \
    --run-mode COHORT \
    -L ${workpath}/gc.filtered.500.interval_list \
    $sample_rc \
    --contig-ploidy-calls ${workpath}/model/ploidy-calls \
    --annotated-intervals ${workpath}/targets.preprocessed.500.annotated_intervals.tsv \
    --interval-merging-rule OVERLAPPING_ONLY \
    --output ${workpath}/model \
    --output-prefix baseline \
    --verbosity DEBUG;then
    echo "Step completed: GermlineCNVCaller"
else
    echo "Error in step: GermlineCNVCaller" >&2
    exit 1
fi
