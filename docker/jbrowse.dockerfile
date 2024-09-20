FROM node:22.2.0-slim
WORKDIR /app
RUN npm install -g @jbrowse/cli serve && jbrowse create /app
RUN mv test_data/volvox data && rm -rf test_data && \
    sed -i -E 's,(<div id="root">),<script>window.__jbrowseConfigPath = "data/config.json";</script>\1,' index.html
CMD ["npx", "serve", "."]



