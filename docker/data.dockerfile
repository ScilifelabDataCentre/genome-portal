ARG NODE_VERSION=24.14.0@sha256:3a09aa6354567619221ef6c45a5051b671f953f0a1924d1f819ffb236e520e6b
ARG NODE_VERSION_SLIM=24.14.0-slim@sha256:e8e2e91b1378f83c5b2dd15f0247f34110e2fe895f6ca7719dbb780f929368eb

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