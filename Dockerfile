FROM python:3.8

LABEL vendor=neon.ai \
    ai.neon.name="neon-enclosure"

ADD . /neon_enclosure
WORKDIR /neon_enclosure

RUN apt update && \
    export CFLAGS="-fcommon" && \
    apt install -y pulseaudio && \
    pip install wheel && \
    pip install \
    holmesV \
    .

RUN useradd -ms /bin/bash neon
USER neon

COPY docker_overlay/asoundrc /home/neon/.asoundrc

RUN mkdir -p /home/neon/.config/pulse && \
    mkdir -p /home/neon/.config/neon && \
    mkdir -p /home/neon/.local/share/neon

CMD ["neon_enclosure_client"]