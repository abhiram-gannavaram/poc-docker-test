# Vulnerable but buildable base
FROM ubuntu:18.04

# Use EOL repository (Ubuntu 18.04) – still supported
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://old-releases.ubuntu.com/ubuntu/|g' /etc/apt/sources.list && \
    sed -i 's|http://security.ubuntu.com/ubuntu|http://old-releases.ubuntu.com/ubuntu|g' /etc/apt/sources.list

# Update and install insecure outdated packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    netcat \
    telnet \
    apache2 && \
    rm -rf /var/lib/apt/lists/*

# Expose insecure ports
EXPOSE 22 23 80

# Install vulnerable Python libraries (WORKING VERSIONS)
RUN pip3 install \
    flask==0.12.4 \
    requests==2.19.1 \
    urllib3==1.24.3

# Weak SSH config (root login)
RUN echo 'root:password' | chpasswd && \
    mkdir /var/run/sshd && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

CMD ["/bin/sh", "-c", "echo 'Vulnerable image for POC' && tail -f /dev/null"]
