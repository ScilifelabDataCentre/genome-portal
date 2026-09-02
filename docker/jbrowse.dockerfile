FROM node:22.23.2-slim@sha256:83f487e0a63425e5b4d146fb5e5be574bcbe1b7b843d3ebafdd95eaf7767a7e5
WORKDIR /app
RUN npm install -g @jbrowse/cli serve && jbrowse create /app
RUN mv test_data/volvox data && rm -rf test_data && \
    sed -i -E 's,(<div id="root">),<script>window.__jbrowseConfigPath = "data/config.json";</script>\1,' index.html
CMD ["npx", "serve", "."]



