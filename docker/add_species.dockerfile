ARG PYTHON_IMAGE_TAG=3.11-slim

# Be careful with bumping Python in this image. Quast v5.3.0 (latest at the time of writing)
# requires distutils, which was removed from the Python standard library in Python 3.12.

# Build tools stage: install Pixi + AGAT, Python venv deps, QUAST, yq, Pandoc.
FROM python:${PYTHON_IMAGE_TAG} AS build_tools

ARG PIXI_VERSION=v0.67.0
ARG PIXI_HOME=/opt/pixi
ARG AGAT_VERSION=1.6.1
ARG PANDAS_VERSION=2.2.3
ARG OPENPYXL_VERSION=3.1.5
ARG PILLOW_VERSION=10.3.0
ARG REQUESTS_VERSION=2.32.4
ARG PYYAML_VERSION=6.0.2
ARG QUAST_VERSION=5.3.0
ARG YQ_VERSION=4.52.5
ARG PANDOC_VERSION=3.9.0.2
ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    tar \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://pixi.sh/install.sh \
    | PIXI_VERSION=${PIXI_VERSION} PIXI_HOME=${PIXI_HOME} PIXI_BIN_DIR=/usr/local/bin PIXI_NO_PATH_UPDATE=1 sh

RUN mkdir -p /opt/agat_workspace \
    && printf '%s\n' \
    '[workspace]' \
    'name = "add-species-tools"' \
    'channels = ["conda-forge", "bioconda"]' \
    'platforms = ["linux-64", "linux-aarch64"]' \
    '' \
    '[dependencies]' \
    "agat = \"==${AGAT_VERSION}\"" \
    > /opt/agat_workspace/pixi.toml \
    && cd /opt/agat_workspace \
    && pixi install

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --upgrade pip \
    && pip install --no-cache-dir \
    pandas==${PANDAS_VERSION} \
    openpyxl==${OPENPYXL_VERSION} \
    Pillow==${PILLOW_VERSION} \
    requests==${REQUESTS_VERSION} \
    pyyaml==${PYYAML_VERSION}

# Install QUAST from GH release since the bioconda recipe has a bug related to distutils deprecation (at the time of writing).
RUN mkdir -p /opt/quast \
    && curl -fsSL -o /tmp/quast.tar.gz \
    https://github.com/ablab/quast/releases/download/quast_${QUAST_VERSION}/quast-${QUAST_VERSION}.tar.gz \
    && tar -xzf /tmp/quast.tar.gz -C /opt/quast \
    && rm -f /tmp/quast.tar.gz \
    && printf '%s\n' '#!/bin/sh' "exec /opt/venv/bin/python /opt/quast/quast-${QUAST_VERSION}/quast.py \"\$@\"" > /usr/local/bin/quast \
    && printf '%s\n' '#!/bin/sh' "exec /opt/venv/bin/python /opt/quast/quast-${QUAST_VERSION}/quast.py \"\$@\"" > /usr/local/bin/quast.py \
    && chmod +x /usr/local/bin/quast /usr/local/bin/quast.py

RUN case "${TARGETARCH}" in \
      amd64|arm64) ;; \
      *) echo "Unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac

RUN curl -fsSL -o /usr/local/bin/yq "https://github.com/mikefarah/yq/releases/download/v${YQ_VERSION}/yq_linux_${TARGETARCH}" \
    && chmod +x /usr/local/bin/yq

RUN curl -fsSL -o /tmp/pandoc.tar.gz \
      "https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-${TARGETARCH}.tar.gz" \
    && tar -xzf /tmp/pandoc.tar.gz -C /tmp \
    && cp "/tmp/pandoc-${PANDOC_VERSION}/bin/pandoc" /usr/local/bin/pandoc \
    && rm -rf /tmp/pandoc.tar.gz "/tmp/pandoc-${PANDOC_VERSION}"

# Final stage: bring in required tools from build_tools.
FROM python:${PYTHON_IMAGE_TAG}

WORKDIR /swedgene

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build_tools /usr/local/bin/yq /usr/local/bin/yq
COPY --from=build_tools /usr/local/bin/pandoc /usr/local/bin/pandoc
COPY --from=build_tools /usr/local/bin/quast /usr/local/bin/quast
COPY --from=build_tools /usr/local/bin/quast.py /usr/local/bin/quast.py
COPY --from=build_tools /opt/venv /opt/venv
COPY --from=build_tools /opt/quast /opt/quast
COPY --from=build_tools /opt/agat_workspace/.pixi/envs/default /opt/agat_env

# Ensure AGAT, QUAST and Python deps venv are available on PATH.
ENV PATH="/opt/venv/bin:/opt/agat_env/bin:${PATH}"

CMD ["python", "scripts/add_new_species", "--help"]
