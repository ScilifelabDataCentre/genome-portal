ARG NODE_VERSION=24.15.0@sha256:e9891237dfbb1de60ce19e9ff9fac5d73ad9c37da303ad72ff2a425ad1057e71
ARG NODE_VERSION_SLIM=24.15.0-slim@sha256:03eae3ef7e88a9de535496fb488d67e02b9d96a063a8967bae657744ecd513f2

# Stage 1: Build
FROM node:${NODE_VERSION} AS build
ARG SAMTOOLS_VERSION="1.20"

RUN curl -fsSL https://github.com/samtools/samtools/releases/download/${SAMTOOLS_VERSION}/samtools-${SAMTOOLS_VERSION}.tar.bz2 \
    | tar -C /tmp -xjf-  \
    && cd /tmp/samtools-${SAMTOOLS_VERSION} && ./configure && make all all-htslib && make install install-htslib \
    && cd - && rm -rf /tmp/samtools-${SAMTOOLS_VERSION}

RUN curl -fsSL --output /usr/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 \
    && chmod +x /usr/bin/yq

# Final stage with slim image to save space
FROM node:${NODE_VERSION_SLIM} 

WORKDIR /swedgene
VOLUME /swedgene/data

RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    curl \
    ca-certificates \
    libdeflate0 \
    libcurl4 \
    libncursesw6 \
    jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/bin/samtools /usr/local/bin/
COPY --from=build /usr/local/bin/htsfile /usr/local/bin/
COPY --from=build /usr/local/bin/bgzip /usr/local/bin/
COPY --from=build /usr/local/bin/tabix /usr/local/bin/
COPY --from=build /usr/bin/yq /usr/bin/

RUN npm install -g @jbrowse/cli

COPY config config
COPY scripts scripts
COPY Makefile .

ARG SWG_UID=1000
ARG SWG_GID=1000
RUN groupmod -g ${SWG_GID} node && usermod -u ${SWG_UID} -g ${SWG_GID} node
ENV SHELL=/bin/sh
USER node

CMD ["make", "debug"]