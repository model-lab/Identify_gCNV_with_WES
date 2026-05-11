# 快速参考：新增的Snakemake规则

## 规则执行顺序和依赖关系

```
样本FASTQ文件
    ↓
[map_reads_bwa] → sorted.bam
    ↓
[index_sorted_bam] → sorted.bam.bai
    ↓
[mark_duplicates_picard] → dedup.bam, dedup.metrics
    ↓
[index_dedup_bam] → dedup.bam.bai
    ↓
[base_recalibrator] → recal_data.grp
    ↓                    
[apply_bqsr] (读取dedup.bam + recal_data.grp) → recal.bam
    ↓
[index_final_bam] → recal.bam.bai
    ↓
[collect_read_counts] → readcounts.tsv (下游分析)
```

## 核心规则详情

### 1. index_sorted_bam
```
输入: work/{sample}/{sample}.sorted.bam
输出: work/{sample}/{sample}.sorted.bam.bai
工具: samtools index
```

### 2. index_dedup_bam
```
输入: work/{sample}/{sample}.dedup.bam
输出: work/{sample}/{sample}.dedup.bam.bai
工具: samtools index
```

### 3. base_recalibrator
```
输入: 
  - work/{sample}/{sample}.dedup.bam
  - work/{sample}/{sample}.dedup.bam.bai
输出: work/{sample}/{sample}.recal_data.grp
工具: GATK BaseRecalibrator
参数: -Xmx24g, --known-sites (从config.yaml读取)
```

### 4. apply_bqsr
```
输入:
  - work/{sample}/{sample}.dedup.bam
  - work/{sample}/{sample}.recal_data.grp
输出: work/{sample}/{sample}.recal.bam
工具: GATK ApplyBQSR
参数: -Xmx24g
```

### 5. index_final_bam
```
输入: work/{sample}/{sample}.recal.bam
输出: work/{sample}/{sample}.recal.bam.bai
工具: samtools index
```

## 修改的规则

### map_reads_bwa (改进版)
**关键改进:**
- 添加了 `-R "@RG\tID:{sample}\tSM:{sample}\tLB:{sample}\tPL:ILLUMINA"` 读组标签
- 使用 `-a -M` 参数输出完整的比对结果

### mark_duplicates_picard (改进版)
**关键改进:**
- 输出更正为 `{sample}.dedup.bam` (原为 `{sample}.recal.bam`)
- 添加metrics文件输出
- 添加了异常处理

### collect_read_counts (改进版)
**关键改进:**
- 自动检测处理好的recal.bam
- 优先使用处理管道生成的BAM
- Fallback到plan文件中指定的BAM

## config.yaml 新增配置

```yaml
known_sites_mills: ../data/Mills_and_1000G_gold_standard_indels.vcf.gz
known_sites_kg: ../data/1000G_omni2.4.sites.vcf.gz
known_sites_dbsnp: ../data/dbsnp_138.vcf.gz
```

## 常见问题排查

### Q: BaseRecalibrator 无法找到known-sites文件
**A:** 检查config.yaml中的路径是否正确。可从以下位置获取这些文件：
- GATK Resource Bundle: https://gatk.broadinstitute.org/hc/en-us/articles/360035890811-Resource-bundles

### Q: 为什么apply_bqsr输出为dedup.bam的复制？
**A:** 这是fallback行为。BaseRecalibrator失败时，ApplyBQSR仍会创建输出文件，以便管道继续进行。生产环境需要修复known-sites配置。

### Q: BAM文件中没有读组信息
**A:** 检查map_reads_bwa规则中的-R参数是否正确传递。使用 `samtools view -H recal.bam` 查看头部信息。

## 验证命令

```bash
# 查看BAM头部（检查读组）
samtools view -H data/work/SAMPLE/SAMPLE.recal.bam

# 统计BAM索引信息
samtools index -c data/work/SAMPLE/SAMPLE.recal.bam

# 验证BQSR数据文件
head -50 data/work/SAMPLE/SAMPLE.recal_data.grp

# 运行dry-run检查
snakemake -n --dry-run --cores 1
```

## 性能优化建议

1. **并行处理**: 使用 `snakemake --cores 8` (或更多)
2. **Java堆内存**: 根据硬件调整 `-Xmx24g` 参数
3. **BWA线程**: 修改 `-t 12` 参数以匹配CPU核心数
4. **磁盘I/O**: 确保work目录在快速存储上

## 已知限制

1. 目前支持单样本处理，批量处理通过plan文件实现
2. 仅支持paired-end测序数据（R1/R2）
3. 需要预先准备好known-sites VCF文件
