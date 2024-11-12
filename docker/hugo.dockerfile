ARG NODE_VERSION=22.2.0
ARG JBROWSE_VERSION=2.15.4

# Stage 1: Download HUGO + build static site. 
FROM alpine:latest AS build

ARG HUGO_VERSION=0.128.2

RUN apk add --no-cache wget

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
ARG JBROWSE_VERSION
ARG HUGO_PORTAL_VERSION=""
ARG HUGO_GIT_BRANCH=""
ARG HUGO_GIT_SHA=""

ARG CI_EVENT_NAME
    CI_GIT_REF_NAME
    CI_GIT_REF
    CI_GIT_SHA

# pass the environment variables to the build
RUN mkdir /target && \
    hugo -d /target --minify --gc


# Stage 2: Install JBrowse
FROM node:${NODE_VERSION}-slim AS jbrowse
ARG JBROWSE_VERSION

WORKDIR /tmp
RUN npm install -g @jbrowse/cli
COPY ./scripts/download_jbrowse .
RUN bash ./download_jbrowse v${JBROWSE_VERSION} /tmp/browser


# Stage 3: Serve the generated html using nginx
FROM nginxinc/nginx-unprivileged:stable-alpine

COPY docker/nginx-custom.conf /etc/nginx/conf.d/default.conf 

COPY --from=build /target /usr/share/nginx/html
COPY --from=jbrowse /tmp/browser /usr/share/nginx/html/browser

EXPOSE 8080
