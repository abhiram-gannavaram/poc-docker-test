# Extremely vulnerable Dockerfile for testing DevSecOps pipeline
# Intentionally uses EOL, unpatched, vulnerable software

# ❌ Outdated & EOL base image (tons of CVEs)
FROM ubuntu:14.04

# ❌ Disable security updates
RUN echo "APT::Get::AllowUnauthenticated \"true\";" >> /etc/apt/apt.conf

# ❌ Use deprecated apt-get upgrade
RUN apt-get update && apt-get upgrade -y

# ❌ Install multiple outdated and vulnerable packages
RUN apt-get install -y --no-install-recommends \
    openssh-server \
    curl \
    wget \
    git \
    openssl \
    python \
    python-pip \
    nginx \
    apache2 \
    netcat \
    telnet \
    vsftpd \
    build-essential \
    libssl1.0.0 \
    libc6 \
    bash && \
    rm -rf /var/lib/apt/lists/*

# ❌ Expose insecure ports publicly
EXPOSE 21 22 23 80 443

# ❌ Allow root login (intentional vulnerability)
RUN mkdir /var/run/sshd && \
    echo 'root:password' | chpasswd && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# ❌ Add vulnerable pip packages
RUN pip install flask==0.10 \
    requests==2.6.0 \
    urllib3==1.13.1

# ❌ Add a file with hardcoded secret key
RUN echo "SECRET_KEY=hardcoded_insecure_key_123" > /etc/myapp.conf

# ❌ Run everything as root
USER root

CMD ["/bin/sh", "-c", "echo 'Vulnerabilities intentionally added for POC testing' && tail -f /dev/null"]
