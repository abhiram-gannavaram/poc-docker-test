# Minimal vulnerable Dockerfile for Trivy + Bedrock testing
FROM python:3.9-slim

# Install known vulnerable Python libraries
RUN pip install \
    flask==1.0 \
    requests==2.19.1 \
    urllib3==1.24.3

# Add a fake secret (intentional vulnerability)
ENV SECRET_KEY="hardcoded-insecure-secret"

# Run as root (vulnerability)
USER root

CMD ["python3", "-c", "print('Vulnerable POC container is running')"]
