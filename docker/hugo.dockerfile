ARG NODE_VERSION=22.2.0

# Stage 1: Download HUGO + build static site. 
FROM alpine:latest AS build
RUN apk add --no-cache wget
ARG HUGO_VERSION="0.138.0"

RUN wget --quiet "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_Linux-64bit.tar.gz" && \
    tar xzf hugo_${HUGO_VERSION}_Linux-64bit.tar.gz && \
    rm -r hugo_${HUGO_VERSION}_Linux-64bit.tar.gz && \
    mv hugo /usr/bin && \
    chmod 755 /usr/bin/hugo

WORKDIR /src
COPY ./hugo/ /src

RUN mkdir /target && \
    hugo -d /target

FROM node:${NODE_VERSION}-slim AS jbrowse
ARG JBROWSE_VERSION=2.15.4
WORKDIR /tmp
RUN npm install -g @jbrowse/cli
COPY ./scripts/download_jbrowse .
RUN bash ./download_jbrowse v${JBROWSE_VERSION} /tmp/browser

# Stage 2: Serve the generated html using nginx
FROM nginxinc/nginx-unprivileged:stable-alpine

COPY docker/nginx-custom.conf /etc/nginx/conf.d/default.conf 

COPY --from=build /target /usr/share/nginx/html
COPY --from=jbrowse /tmp/browser /usr/share/nginx/html/browser

EXPOSE 8080
