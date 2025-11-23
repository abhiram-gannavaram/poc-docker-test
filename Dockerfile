# Dockerfile (test-vulnerable)
# Keep ubuntu:22.04 base but add deliberately old language deps for scanner detection.
# TEST ONLY — do not publish images created from this to public registries.

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install basic tooling + node & python so we can add vulnerable language deps.
# Use apt packages for simplicity in CI. Keep commands robust to transient failures.
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
      npm \
    && rm -rf /var/lib/apt/lists/*

# Ensure /app exists and copy manifests from the build context.
# IMPORTANT: package.json and requirements.txt must be present in the build context (repo root by default).
COPY ./package.json /app/package.json
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

# Install the vulnerable dependencies (old versions in the manifests)
# Use "|| true" to let the build continue if a package manager reports a non-zero code
# (keeps CI flow smooth for intentionally broken/vulnerable manifests).
RUN npm install --no-audit --no-fund --production || true
RUN pip3 install --no-cache-dir -r requirements.txt || true

# Minimal runnable artifact so the image can start.
RUN printf "console.log('vuln-sample');" > /app/index.js

EXPOSE 8080

CMD ["node", "/app/index.js"]
