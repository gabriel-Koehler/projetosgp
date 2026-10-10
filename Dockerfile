FROM node:24-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package.json package-lock.json requirements.txt ./
RUN npm ci --omit=dev && python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY public ./public
COPY views ./views
COPY server.js ./
COPY scripts/start-hosted.js ./scripts/start-hosted.js
ENV PATH="/opt/venv/bin:$PATH" HOST=0.0.0.0 PORT=3000
USER node
EXPOSE 3000
CMD ["node", "scripts/start-hosted.js"]
