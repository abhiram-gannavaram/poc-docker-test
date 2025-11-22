# Dockerfile with intentional vulnerabilities
# Using an outdated base image (Ubuntu 16.04) with known CVEs
FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openssh-server \
    curl \
    wget \
    git && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 22

CMD ["/bin/sh", "-c", "echo 'This image has known OS and library vulnerabilities from Ubuntu 16.04'"]
