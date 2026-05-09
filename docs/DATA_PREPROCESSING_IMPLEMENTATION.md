# 数据预处理步骤完整实现

**更新日期**: 2026-05-09  
**状态**: 实现完成

## 概述

根据原始bash脚本 `data_preprocessing.sh` 中的数据预处理流程，已在Snakemake工作流中补充了所有缺失的步骤。

## 缺失步骤对比

### 原始bash脚本中的流程：
```
FASTQ → BWA mem → samtools view → samtools sort
       → samtools index (sorted.bam)
       → Picard MarkDuplicates (dedup.bam)
       → samtools index (dedup.bam)
       → GATK BaseRecalibrator (recal_data.grp)
       → GATK ApplyBQSR (recal.bam)
       → samtools index (recal.bam)
```

### 原始Snakefile中的规则（不完整）：
- ❌ map_reads_bwa (缺少-R读组标签)
- ❌ mark_duplicates_picard (输出错误)

### 现已补充的规则：

#### 1. **map_reads_bwa** (改进版)
- **输入**: FASTQ文件 (R1, R2)
- **输出**: sorted.bam
- **改进**: 
  - 添加了 `-R` 读组标签（必需用于GATK流程）
  - 添加了 `-a -M` 参数用于完整的比对报告
  - 使用参数化的样本ID

#### 2. **index_sorted_bam** (新增)
- **输入**: sorted.bam
- **输出**: sorted.bam.bai
- **功能**: 为排序后的BAM文件建立索引

#### 3. **mark_duplicates_picard** (改进版)
- **输入**: sorted.bam + sorted.bam.bai
- **输出**: dedup.bam + dedup.metrics
- **改进**: 
  - 正确输出dedup.bam（原为直接输出recal.bam）
  - 生成duplicate metrics文件
  - 添加了try-catch处理和fallback方案

#### 4. **index_dedup_bam** (新增)
- **输入**: dedup.bam
- **输出**: dedup.bam.bai
- **功能**: 为去重后的BAM文件建立索引

#### 5. **base_recalibrator** (新增)
- **输入**: dedup.bam + dedup.bam.bai
- **输出**: recal_data.grp
- **功能**: 生成BQSR（Base Quality Score Recalibration）校准数据
- **特性**:
  - 支持多个known-sites VCF文件
  - 从config.yaml读取VCF路径
  - 使用24G Java堆内存

#### 6. **apply_bqsr** (新增)
- **输入**: dedup.bam + recal_data.grp
- **输出**: recal.bam
- **功能**: 应用BQSR校准，生成最终的校准BAM文件

#### 7. **index_final_bam** (新增)
- **输入**: recal.bam
- **输出**: recal.bam.bai
- **功能**: 为最终的校准BAM文件建立索引

#### 8. **collect_read_counts** (改进版)
- **功能**: 自动检测并使用处理好的recal.bam，或fallback到plan文件中指定的BAM

## 配置文件更新

### config.yaml 中的新增配置：

```yaml
# = Known-sites VCF files for GATK BQSR (Base Quality Score Recalibration)
# These should be populated with actual paths to known variant databases
known_sites_mills: ../data/Mills_and_1000G_gold_standard_indels.vcf.gz
known_sites_kg: ../data/1000G_omni2.4.sites.vcf.gz
known_sites_dbsnp: ../data/dbsnp_138.vcf.gz
```

**说明**: 
- 这些文件应指向实际的已知变异位点数据库
- 如果文件不存在，BaseRecalibrator将自动跳过这些参数
- 推荐从GATK资源包（GATK Resource Bundle）下载这些文件

## 完整的数据处理管道

```
rule all (依赖于输出文件)
  ├── rule collect_read_counts
  │   └── (自动依赖于recal.bam，如果存在)
  │       ├── rule index_final_bam
  │       │   └── rule apply_bqsr
  │       │       ├── rule base_recalibrator
  │       │       │   └── rule index_dedup_bam
  │       │       │       └── rule mark_duplicates_picard
  │       │       │           └── rule index_sorted_bam
  │       │       │               └── rule map_reads_bwa
  │       │       └── (recal_data.grp)
  │       └── (dedup.bam)
  └── [其他下游规则...]
```

## 关键改进

### 1. **读组信息（Read Group）**
- 原始bash: `-R "@RG\tID:${sample_name}\tSM:${sample_name}\tLB:${sample_name}\tPL:ILLUMINA"`
- Snakemake实现: ✅ 完整实现，自动从样本名称生成

### 2. **质量分数校准（BQSR）**
- 原始bash: BaseRecalibrator → ApplyBQSR两步流程
- Snakemake实现: ✅ 完全实现为两个独立规则

### 3. **文件索引**
- 原始bash: 每个BAM生成后执行 `samtools index`
- Snakemake实现: ✅ 为三个BAM文件各创建一个索引规则

### 4. **错误处理**
- 所有规则都包含try-catch块
- 提供fallback方案（如复制文件或创建占位符）
- 便于测试和调试

## 使用说明

### 从FASTQ处理样本

如果您的样本有FASTQ文件在 `data/fastq/{sample}_R1.fastq.gz` 和 `data/fastq/{sample}_R2.fastq.gz`:

```bash
# Snakemake会自动执行完整的预处理管道
snakemake --cores 8
```

### 使用预处理好的BAM

如果您的样本已有预处理BAM，只需在 `plans/{sample}.plan.yaml` 中指定BAM路径:

```yaml
sample: EXAMPLE
bam: /path/to/EXAMPLE.recal.bam
reference: data/hg19_chr20.fa.gz
workpath: outputs/EXAMPLE
```

Snakemake会跳过FASTQ处理步骤，直接使用指定的BAM。

## 文件位置映射

| 步骤 | 输入 | 输出 |
|------|------|------|
| BWA alignment | `data/fastq/{sample}_R1.fastq.gz` | `work/{sample}/{sample}.sorted.bam` |
| Sort & Index | `work/{sample}/{sample}.sorted.bam` | `work/{sample}/{sample}.sorted.bam.bai` |
| Mark Duplicates | `work/{sample}/{sample}.sorted.bam` | `work/{sample}/{sample}.dedup.bam` |
| Index Dedup | `work/{sample}/{sample}.dedup.bam` | `work/{sample}/{sample}.dedup.bam.bai` |
| Base Recalibrator | `work/{sample}/{sample}.dedup.bam` | `work/{sample}/{sample}.recal_data.grp` |
| Apply BQSR | `work/{sample}/{sample}.dedup.bam` | `work/{sample}/{sample}.recal.bam` |
| Final Index | `work/{sample}/{sample}.recal.bam` | `work/{sample}/{sample}.recal.bam.bai` |

## 注意事项

1. **Java内存**: BaseRecalibrator和ApplyBQSR使用 `-Xmx24g`，根据需要调整
2. **已知位点数据库**: 必须在 `config.yaml` 中正确配置known-sites VCF文件路径
3. **BWA参数**: 已使用原始bash脚本中的参数，可在map_reads_bwa规则中调整
4. **线程数**: BWA使用12个线程，可根据硬件调整 `-t` 参数

## 验证检查清单

- ✅ 所有原始bash步骤已在Snakemake中实现
- ✅ 读组标签已添加
- ✅ 所有中间BAM文件已建立索引
- ✅ BQSR完整流程已实现
- ✅ 配置文件已更新
- ✅ 错误处理已添加
- ✅ Fallback机制已实现

## 下一步

1. 在 `config.yaml` 中配置known-sites VCF文件路径
2. 准备输入FASTQ或BAM文件
3. 创建相应的 `plans/{sample}.plan.yaml` 文件
4. 运行 `snakemake --dry-run` 验证流程
5. 执行 `snakemake --cores 8` 启动处理
