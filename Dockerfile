# Small and vulnerable Dockerfile for testing
FROM python:3.8-slim

# Install vulnerable OS packages
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    telnet \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Install outdated & vulnerable Python packages
RUN pip install \
    flask==1.0 \
    requests==2.19.1 \
    urllib3==1.24.3

# Deliberately run as root (vulnerability)
USER root

CMD ["python3", "-c", "print('Vulnerable test container running')"]
