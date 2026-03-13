FROM node:22.22.1-slim@sha256:9c2c405e3ff9b9afb2873232d24bb06367d649aa3e6259cbe314da59578e81e9
WORKDIR /app
RUN npm install -g @jbrowse/cli serve && jbrowse create /app
RUN mv test_data/volvox data && rm -rf test_data && \
    sed -i -E 's,(<div id="root">),<script>window.__jbrowseConfigPath = "data/config.json";</script>\1,' index.html
CMD ["npx", "serve", "."]



