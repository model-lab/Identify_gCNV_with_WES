# Base image
FROM continuumio/miniconda3

# Set working directory
WORKDIR /workspace

# Install dependencies
RUN conda install -y -c bioconda gatk=4.2.0.0 && \
    conda clean -a

# Copy workflow files
COPY . /workspace

# Set entrypoint
ENTRYPOINT ["snakemake"]