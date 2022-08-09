FROM python:3.8-slim

LABEL vendor=neon.ai \
    ai.neon.name="neon-enclosure"

ENV NEON_CONFIG_PATH /config

ADD . /neon_enclosure
WORKDIR /neon_enclosure

RUN apt update && \
    export CFLAGS="-fcommon" && \
    apt install -y pulseaudio && \
    pip install wheel && \
    pip install .

COPY docker_overlay/ /

CMD ["neon_enclosure_client"]