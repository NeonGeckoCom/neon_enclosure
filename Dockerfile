FROM python:3.8-slim

LABEL vendor=neon.ai \
    ai.neon.name="neon-enclosure"

ENV NEON_CONFIG_PATH /config

RUN apt update && \
    apt install -y pulseaudio git gcc portaudio19-dev

ADD . /neon_enclosure
WORKDIR /neon_enclosure

RUN pip install wheel && \
    pip install .[docker]

COPY docker_overlay/ /

CMD ["neon_enclosure_client"]