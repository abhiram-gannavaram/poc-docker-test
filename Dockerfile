# ABSOLUTE MINIMAL ALWAYS-BUILD DOCKERFILE (intentionally vulnerable)

FROM busybox:latest

# Add an insecure file with a hardcoded secret
RUN echo "SECRET_KEY=super-insecure-hardcoded-key" > /etc/secret.env

# Bad practice: running as root (default)
USER root

# Another vulnerability: world-readable secrets
RUN chmod 777 /etc/secret.env

CMD ["sh", "-c", "echo Vulnerable container running"]
