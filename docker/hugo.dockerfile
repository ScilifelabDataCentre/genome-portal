ARG NODE_VERSION=22.2.0
ARG JBROWSE_VERSION=4.1.15
ARG GWAS_PLUGIN_VERSION=2.1.4

## Stage 1: Download HUGO + build static site. 

# Use debian instead of alpine for build to avoid a MacOS + Rancher desktop build issue.
FROM debian:stable-slim@sha256:85dfcffff3c1e193877f143d05eaba8ae7f3f95cb0a32e0bc04a448077e1ac69 AS build

ARG HUGO_VERSION=0.138.0
ARG JBROWSE_VERSION

RUN apt-get update && apt-get install -y --no-install-recommends wget ca-certificates jq && rm -rf /var/lib/apt/lists/*

RUN wget --quiet "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_Linux-64bit.tar.gz" && \
    tar xzf hugo_${HUGO_VERSION}_Linux-64bit.tar.gz && \
    rm -r hugo_${HUGO_VERSION}_Linux-64bit.tar.gz && \
    mv hugo /usr/bin && \
    chmod 755 /usr/bin/hugo

WORKDIR /src
COPY ./hugo/ /src

# Docker build arguments (passed in Github actions for example) take
# precendence over these values. These variables are available in the
# environment of subsequent RUN instructions
ARG HUGO_JBROWSE_VERSION=${JBROWSE_VERSION}
ARG HUGO_GIT_REF_NAME
ARG HUGO_GIT_SHA

# Generate the metrics file before building the hugo site, so that the metrics are included in the generated static files.
COPY ./scripts/generate_metrics.sh /usr/local/bin/generate_metrics.sh
RUN ROOT_DIR=/src bash /usr/local/bin/generate_metrics.sh

# pass the environment variables to the build
# On MacOS with Rancher desktop, the build VM can run out of memory when building the hugo image, causing a crash in Go's lfstack implementation. 
# Setting GOGC=off disables Go's runtime GC, working around this issue.

RUN mkdir /target && \
    GOGC=off hugo -d /target --minify --gc


## Stage 2: Install JBrowse and GWAS plugin
FROM node:${NODE_VERSION}-slim AS jbrowse
ARG JBROWSE_VERSION
ARG GWAS_PLUGIN_VERSION

WORKDIR /tmp

# Note! The JBrowse CLI is installed from npm, and is then to fetch the prebuilt JBrowse web release assets from GitHub for the same pinned version.
# There has been an example where the npm packages was available but the GH release had been deleted. The fix was to bump the JBrowse version.
RUN npm install -g @jbrowse/cli@${JBROWSE_VERSION}
COPY ./scripts/download_jbrowse .
RUN bash ./download_jbrowse v${JBROWSE_VERSION} /tmp/browser

# Download pinned version of jbrowse-plugin-gwas and bundle it with the image
RUN mkdir -p /tmp/browser/plugins /tmp/gwas-plugin-stage && \
    npm pack "jbrowse-plugin-gwas@${GWAS_PLUGIN_VERSION}" --pack-destination /tmp && \
    tar -xzf "/tmp/jbrowse-plugin-gwas-${GWAS_PLUGIN_VERSION}.tgz" -C /tmp/gwas-plugin-stage --strip-components=1 && \
    cp /tmp/gwas-plugin-stage/dist/jbrowse-plugin-gwas.umd.production.min.js /tmp/browser/plugins/


## Stage 3: Serve the generated html using nginx
FROM nginxinc/nginx-unprivileged:stable-alpine@sha256:7377697a821c131a924a7105fafbe7414db4e9fcc77a6f08f776f33f141ec3f8

COPY docker/nginx-custom.conf /etc/nginx/conf.d/default.conf 

COPY --from=build /target /usr/share/nginx/html
COPY --from=jbrowse /tmp/browser /usr/share/nginx/html/browser

EXPOSE 8080
