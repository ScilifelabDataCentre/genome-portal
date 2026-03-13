FROM node:24.14.0-slim@sha256:e8e2e91b1378f83c5b2dd15f0247f34110e2fe895f6ca7719dbb780f929368eb
WORKDIR /app
RUN npm install -g @jbrowse/cli serve && jbrowse create /app
RUN mv test_data/volvox data && rm -rf test_data && \
    sed -i -E 's,(<div id="root">),<script>window.__jbrowseConfigPath = "data/config.json";</script>\1,' index.html
CMD ["npx", "serve", "."]



