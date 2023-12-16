FROM python:3.8-slim

LABEL vendor=neon.ai \
    ai.neon.name="neon-enclosure"

ENV OVOS_CONFIG_BASE_FOLDER neon
ENV OVOS_CONFIG_FILENAME neon.yaml
ENV XDG_CONFIG_HOME /config

RUN apt update && \
    apt install -y  \
    pulseaudio  \
    git  \
    gcc  \
    portaudio19-dev

ADD . /neon_enclosure
WORKDIR /neon_enclosure

RUN pip install wheel && \
    pip install .[docker]

COPY docker_overlay/ /

CMD ["neon-enclosure", "run"]