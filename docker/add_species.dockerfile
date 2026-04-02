ARG MICROMAMBA_TAG=2.5.0-debian12
ARG PYTHON_IMAGE_TAG=3.12-slim

# Build stage 1: Conda-only build stage. Install agat through conda since its dependencies are complex
FROM mambaorg/micromamba:${MICROMAMBA_TAG} AS conda_tools

ARG CONDA_CHANNEL_PRIMARY=conda-forge
ARG CONDA_CHANNEL_BIO=bioconda
ARG CONDA_ENV_NAME=add-species-tools
ARG CONDA_PYTHON_VERSION=3.11
ARG AGAT_VERSION=1.6.1

RUN micromamba create -y -n ${CONDA_ENV_NAME} \
    -c ${CONDA_CHANNEL_PRIMARY} \
    -c ${CONDA_CHANNEL_BIO} \
    --override-channels \
    --strict-channel-priority \
    python=${CONDA_PYTHON_VERSION} \
    agat=${AGAT_VERSION} \
    && micromamba clean --all --yes

# Build stage 2
FROM python:${PYTHON_IMAGE_TAG} AS non_conda_build

ARG CONDA_ENV_NAME=add-species-tools
ARG PANDAS_VERSION=2.2.3
ARG OPENPYXL_VERSION=3.1.5
ARG PILLOW_VERSION=10.3.0
ARG REQUESTS_VERSION=2.32.4
ARG PYYAML_VERSION=6.0.2
ARG QUAST_VERSION=5.3.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --upgrade pip \
    && pip install --no-cache-dir \
    pandas==${PANDAS_VERSION} \
    openpyxl==${OPENPYXL_VERSION} \
    Pillow==${PILLOW_VERSION} \
    requests==${REQUESTS_VERSION} \
    pyyaml==${PYYAML_VERSION}

# quast requres distutils, which is not included in Python 3.12 and was not correctly resolved by conda, so make it use Python 3.11 from the conda env after installation. 
RUN mkdir -p /opt/quast \
    && curl -fsSL -o /tmp/quast.tar.gz \
    https://github.com/ablab/quast/releases/download/quast_${QUAST_VERSION}/quast-${QUAST_VERSION}.tar.gz \
    && tar -xzf /tmp/quast.tar.gz -C /opt/quast \
    && rm -f /tmp/quast.tar.gz \
    && printf '%s\n' '#!/bin/sh' "exec /opt/conda/envs/${CONDA_ENV_NAME}/bin/python /opt/quast/quast-${QUAST_VERSION}/quast.py \"\$@\"" > /usr/local/bin/quast \
    && printf '%s\n' '#!/bin/sh' "exec /opt/conda/envs/${CONDA_ENV_NAME}/bin/python /opt/quast/quast-${QUAST_VERSION}/quast.py \"\$@\"" > /usr/local/bin/quast.py \
    && chmod +x /usr/local/bin/quast /usr/local/bin/quast.py
RUN curl -fsSL -o /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 \
    && chmod +x /usr/local/bin/yq

# Final stage: install pandoc and bring in required tools from previous stages
FROM python:${PYTHON_IMAGE_TAG}

ARG CONDA_ENV_NAME=add-species-tools
ARG PANDOC_VERSION=3.9.0.2
ARG TARGETARCH

WORKDIR /swedgene

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    tar \
    && rm -rf /var/lib/apt/lists/*

RUN case "${TARGETARCH}" in \
      amd64) PANDOC_ARCH="amd64" ;; \
      arm64) PANDOC_ARCH="arm64" ;; \
      *) echo "Unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && curl -fsSL -o /tmp/pandoc.tar.gz \
      "https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-${PANDOC_ARCH}.tar.gz" \
    && tar -xzf /tmp/pandoc.tar.gz -C /tmp \
    && cp "/tmp/pandoc-${PANDOC_VERSION}/bin/pandoc" /usr/local/bin/pandoc \
    && rm -rf /tmp/pandoc.tar.gz "/tmp/pandoc-${PANDOC_VERSION}"

COPY --from=non_conda_build /usr/local/bin/yq /usr/local/bin/yq
COPY --from=non_conda_build /usr/local/bin/quast /usr/local/bin/quast
COPY --from=non_conda_build /usr/local/bin/quast.py /usr/local/bin/quast.py
COPY --from=non_conda_build /opt/venv /opt/venv
COPY --from=non_conda_build /opt/quast /opt/quast

# Bring in only the conda environment that contains AGAT.
COPY --from=conda_tools /opt/conda/envs/${CONDA_ENV_NAME} /opt/conda/envs/${CONDA_ENV_NAME}

# Ensure AGAT, QUAST and Python deps venv are available on PATH.
ENV PATH="/opt/venv/bin:/opt/conda/envs/${CONDA_ENV_NAME}/bin:${PATH}"

CMD ["python", "scripts/add_new_species", "--help"]
