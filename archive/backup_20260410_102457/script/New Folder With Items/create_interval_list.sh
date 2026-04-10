#!/bin/bash


# Define variables
reference="path_to_reference"
ucsc_exon_interval="path_to_ucsc_refgene"

samtools dict ${reference} > ${reference}.dict

awk -F"\t" 'NR == FNR {
    print
    next
}
FNR > 1 && NR > FNR && $3 == "chr20" {
    split($10, start, ",")
    split($11, end, ",")
    gsub("chr", "", $3)
    for (i = 1; i <= $9; i++) {
        print $3 "\t" start[i] "\t" end[i] "\t" $13 "_" i
    }
}' ${reference}.dict ${ucsc_exon_interval} > ${reference}.interval_list
