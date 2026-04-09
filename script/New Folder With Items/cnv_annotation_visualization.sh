cd /path/to/install/knotAnnotSV
configFile=/path/to/install/knotAnnotSV/config_AnnotSV.yaml #(default)
annotSVfile=/path/to/cnv_gvcf_clustered.annotated.tsv
genomeBuild=hg19

perl ./knotAnnotSV.pl \
    --configFile $configFile \
    --annotSVfile $annotSVfile \
    --outDir . \
    --outPrefix test \
    --genomeBuild hg19 \
    --LOEUFcolorRange 1 \
    --datatableDir DataTables
  
  cd /path/to/install/knotAnnotSV

perl ./knotAnnotSV2XL.pl \
    --configFile $configFile \
    --annotSVfile $annotSVfile \
    --outDir . \
    --outPrefix test \
    --genomeBuild hg19 \
    --LOEUFcolorRange 1 \
    --datatableDir DataTables
  