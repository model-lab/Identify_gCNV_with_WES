#!/bin/bash

# Define variables
reference="path_to_reference_genome"
workpath="path_to_work_directory"
picard="path_to_picard.jar"
gatk="path_to_gatk"
Mills_and_1000G_gold_standard_indels="path_to_Mills_and_1000G_gold_standard_indels.vcf"
KG_phase1_snp="path_to_KG_phase1_snp.vcf"
dbsnp138="path_to_dbsnp138.vcf"
samples=("sample1" "sample2" "sample3") # Add all sample names here

for sample_name in "${samples[@]}"; do
  # BWA alignment, sorting, marking duplicates, and indexing
  bwa mem -a -M -t 12 -O 5 -E 3 -R "@RG\tID:${sample_name}\tSM:${sample_name}\tLB:${sample_name}\tPL:ILLUMINA" \
    ${reference} \
    ${workpath}/${sample_name}_val_1.fq.gz ${workpath}/${sample_name}_val_2.fq.gz | \
    samtools view -b -o ${workpath}/${sample_name}.bam && \
    samtools sort -@ 8 -o ${workpath}/${sample_name}.sort.bam ${workpath}/${sample_name}.bam && \
    rm ${workpath}/${sample_name}.bam && \
    samtools index ${workpath}/${sample_name}.sort.bam && \
    java -Xmx24g -jar ${picard} MarkDuplicates \
      INPUT=${workpath}/${sample_name}.sort.bam OUTPUT=${workpath}/${sample_name}.dedup.bam METRICS_FILE=${workpath}/${sample_name}.dedup.metrics && \
    echo "---finish remove duplicates for ${sample_name}---" && \
    samtools index ${workpath}/${sample_name}.dedup.bam && \
    echo "---generate bam index for unified genotype for ${sample_name}---" && \
    
    # Base Recalibration
    ${gatk} --java-options -Xmx24g BaseRecalibrator \
      -R ${reference} \
      -I ${workpath}/${sample_name}.dedup.bam \
      --known-sites ${Mills_and_1000G_gold_standard_indels} \
      --known-sites ${KG_phase1_snp} \
      --known-sites ${dbsnp138} \
      -O ${workpath}/${sample_name}.recal_data.grp && \
    echo "---Finish BaseRecalibrator for ${sample_name}---" && \

    ${gatk} --java-options -Xmx24g ApplyBQSR \
      -R ${reference} \
      -I ${workpath}/${sample_name}.dedup.bam \
      -bqsr ${workpath}/${sample_name}.recal_data.grp \
      -O ${workpath}/${sample_name}.recal.bam && \
    echo "---finish recal with BQSR for ${sample_name}---" && \
    
    samtools index ${workpath}/${sample_name}.recal.bam && \
    echo "---generate bam index for unified genotype for ${sample_name}---"
done

