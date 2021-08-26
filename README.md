# Neon Enclosure
Enclosure module to handle any core interactions with hardware, including volume controls,
lights, buttons, etc.

## Running in Docker
The included `Dockerfile` may be used to build a docker container for the neon_audio module. The below command may be used
to start the container.

```
docker run -d \
--network=host \
-v ~/.local/share/neon:/home/neon/.local/share/neon:rw \
-v ~/.config/neon:/home/neon/.config/neon:rw \
-v ~/.local/share/tts:/home/neon/.local/share/tts \
-v ~/.config/pulse/cookie:/home/mycroft/.config/pulse/cookie:ro \
-v ${XDG_RUNTIME_DIR}/pulse:${XDG_RUNTIME_DIR}/pulse:ro \
--device=/dev/snd:/dev/snd \
-e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
-e PULSE_COOKIE=/home/neon/.config/pulse/cookie \
neon_enclosure
```
