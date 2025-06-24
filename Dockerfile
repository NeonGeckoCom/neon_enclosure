FROM python:3.10-slim

LABEL vendor=neon.ai \
    ai.neon.name="neon-enclosure"

ENV OVOS_CONFIG_BASE_FOLDER=neon
ENV OVOS_CONFIG_FILENAME=neon.yaml
ENV XDG_CONFIG_HOME=/config

RUN apt-get update && \
    apt-get install -y  \
    curl \
    jq \
    pulseaudio  \
    git  \
    gcc  \
    portaudio19-dev

COPY . /neon_enclosure
WORKDIR /neon_enclosure

RUN pip install --no-cache-dir wheel && \
    pip install --no-cache-dir .[docker]

COPY docker_overlay/ /

RUN neon-enclosure install-dependencies
HEALTHCHECK CMD "/opt/neon/healthcheck.sh"
CMD ["bash", "/root/run.sh"]
