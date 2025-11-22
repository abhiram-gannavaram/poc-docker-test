# Dockerfile (updated)
# Uses a supported base image and avoids pinning fragile package versions.
FROM ubuntu:22.04

# Install common tooling without pinning to specific (old) versions.
# Keep `Dockerfile.orig` as a backup of the previous intentionally-vulnerable image.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openssh-server \
    curl \
    wget \
    git && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 22

# Note: container does not configure or run sshd by default. Start sshd if you need SSH access.
CMD ["/bin/sh", "-c", "echo 'Image updated: ubuntu:22.04, packages installed without pinned versions.'"]
