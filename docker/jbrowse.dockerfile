FROM node:22.22.2-slim@sha256:80fdb3f57c815e1b638d221f30a826823467c4a56c8f6a8d7aa091cd9b1675ea
WORKDIR /app
RUN npm install -g @jbrowse/cli serve && jbrowse create /app
RUN mv test_data/volvox data && rm -rf test_data && \
    sed -i -E 's,(<div id="root">),<script>window.__jbrowseConfigPath = "data/config.json";</script>\1,' index.html
CMD ["npx", "serve", "."]



