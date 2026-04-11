# Dockerfile for workflow developer image
FROM continuumio/miniconda3

WORKDIR /workspace

# Copy environment spec and create the conda env
COPY environment.yml /workspace/
RUN conda config --set always_yes yes --set changeps1 no \
    && conda update -n base -c defaults conda \
    && conda env create -f environment.yml \
    && conda clean -afy

# Ensure the environment is on PATH
ENV PATH /opt/conda/envs/cnv_workflow/bin:$PATH

# Copy repository into container
COPY . /workspace

# Default to an interactive shell so users can run make targets or snakemake
ENTRYPOINT ["/bin/bash"]