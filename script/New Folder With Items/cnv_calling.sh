#!/bin/bash

# Activate the conda environment
eval "$(conda shell.bash hook)"
conda activate gatk

# Define variables
reference="path_to_reference_genome" # hg19_chr20.fa, in this protocol"
reference_dict="path_to_reference_sequence_dictionary" # (hg19_chr20.dict, in this protocol)"
interval="path_to_interval_file" # Using the filtered interval files from the output of cnv_model_training.sh, e.g. targets.preprocessed.500.interval_list
workpath="path_to_work_directory"
bam="path_to_bam_file"
gatk="path_to_gatk"
model="path_to_model" # Using the constructed models from the output of cnv_model_training.sh

# Extract sample name from BAM file
samplename=$(basename $bam .bam)

# Collect read counts
if $gatk CollectReadCounts \
    -L $interval \
    -R $reference \
    -imr OVERLAPPING_ONLY \
    -I $bam \
    --format TSV \
    -O ${workpath}/${samplename}.readcounts.tsv; then
    echo "CollectReadCounts completed successfully for $samplename"
else
    echo "CollectReadCounts failed for $samplename" >&2
    exit 1
fi

# Determine germline contig ploidy
if $gatk DetermineGermlineContigPloidy \
    --model ${model}/ploidy-model \
    -I ${workpath}/${samplename}.readcounts.tsv \
    -O ${workpath} \
    --output-prefix ploidy-case \
    --verbosity DEBUG; then
    echo "DetermineGermlineContigPloidy completed successfully for $samplename"
else
    echo "DetermineGermlineContigPloidy failed for $samplename" >&2
    exit 1
fi

# Call germline CNVs
if $gatk GermlineCNVCaller \
    --run-mode CASE \
    -I ${workpath}/${samplename}.readcounts.tsv \
    --contig-ploidy-calls ${workpath}/ploidy-case-calls \
    --model ${model}/baseline-model \
    --output ${workpath} \
    --output-prefix ${samplename} \
    --verbosity DEBUG; then
    echo "GermlineCNVCaller completed successfully for $samplename"
else
    echo "GermlineCNVCaller failed for $samplename" >&2
    exit 1
fi

# Postprocess germline CNV calls
if $gatk PostprocessGermlineCNVCalls \
    --model-shard-path ${model}/baseline-model \
    --calls-shard-path ${workpath}/${samplename}-calls \
    --allosomal-contig chrX --allosomal-contig chrY \
    --contig-ploidy-calls ${workpath}/ploidy-case-calls \
    --sample-index 0 \
    --output-genotyped-intervals ${workpath}/${samplename}.genotyped-intervals.vcf.gz \
    --output-genotyped-segments ${workpath}/${samplename}.genotyped-segments.vcf.gz \
    --output-denoised-copy-ratios ${workpath}/${samplename}.denoised-copy-ratios.txt \
    --sequence-dictionary $reference_dict; then
    echo "PostprocessGermlineCNVCalls completed successfully for $samplename"
else
    echo "PostprocessGermlineCNVCalls failed for $samplename" >&2
    exit 1
fi
