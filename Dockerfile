# Dockerfile (test-vulnerable)
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install basic tooling + Node & Python pip (we install via apt for simplicity in CI)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      wget \
      git \
      ca-certificates \
      gnupg \
      python3 \
      python3-pip \
      nodejs \
      npm && \
    rm -rf /var/lib/apt/lists/*

# Copy intentionally vulnerable language dependency manifests
# (These files declare older, known-vulnerable versions)
COPY package.json /app/package.json
COPY requirements.txt /app/requirements.txt
WORKDIR /app

# Install the language dependencies (these introduce vulnerabilities for scanners)
# Use npm ci/npm install and pip to create a node_modules / site-packages layer.
RUN npm install --no-audit --no-fund --production || true
RUN pip3 install --no-cache-dir -r requirements.txt || true

# Add a tiny app file so the image is runnable (no network access required)
RUN printf "console.log('test');" > /app/index.js

EXPOSE 8080

CMD ["node", "/app/index.js"]
