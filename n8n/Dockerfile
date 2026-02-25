FROM n8nio/n8n:latest

USER root

# Create workflows folder
RUN mkdir -p /home/node/.n8n/workflows \
    && chown -R node:node /home/node/.n8n

# Copy workflow and init script
COPY workflows /home/node/.n8n/workflows
COPY init-n8n.sh /init-n8n.sh

RUN chmod +x /init-n8n.sh \
    && chown node:node /init-n8n.sh

USER node

ENTRYPOINT ["tini", "--"]

CMD sh -c "n8n start & sleep 10 && /init-n8n.sh && wait"