# Dockerfile (updated)
# Dockerfile with intentional vulnerabilities
# Using an extremely outdated base image (Ubuntu 16.04) with known CVEs
FROM ubuntu:22.04

# Use supported base and avoid pinning exact package versions (fragile).
# If you specifically need the old, pinned Ubuntu 16.04 environment for Bedrock
# testing, see `Dockerfile.orig` and `Dockerfile.bak` (both backups of the original).
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
