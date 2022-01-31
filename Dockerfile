FROM python:3.8-slim

LABEL vendor=neon.ai \
    ai.neon.name="neon-enclosure"

ENV NEON_CONFIG_PATH /config

RUN apt update && \
    apt install -y  \
    pulseaudio \
    gcc

ADD . /neon_enclosure
WORKDIR /neon_enclosure

RUN export CFLAGS="-fcommon" && \
    pip install wheel && \
    pip install .[docker]

COPY docker_overlay/asoundrc /home/neon/.asoundrc

#RUN mkdir -p /home/neon/.config/pulse && \
#    mkdir -p /home/neon/.config/neon && \
#    mkdir -p /home/neon/.local/share/neon

CMD ["neon_enclosure_client"]