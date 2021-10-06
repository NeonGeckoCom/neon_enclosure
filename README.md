# Neon Enclosure
Enclosure module to handle any core interactions with hardware, including volume controls,
lights, buttons, etc.

## Running in Docker
The included `Dockerfile` may be used to build a docker container for the neon_audio module. The below command may be used
to start the container.

```shell
docker run -d \
--network=host \
--name=neon_enclosure \
-v ${NEON_DATA_DIR}:/home/neon/.local/share/neon:rw \
-v ${NEON_CONFIG_DIR}:/home/neon/.config/neon:rw \
-v ~/.config/pulse/cookie:/home/neon/.config/pulse/cookie:ro \
-v ${XDG_RUNTIME_DIR}/pulse:${XDG_RUNTIME_DIR}/pulse:ro \
--device=/dev/snd:/dev/snd \
-e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
-e PULSE_COOKIE=/home/neon/.config/pulse/cookie \
neon_enclosure
```

>*Note:* The above example assumes Docker data is stored in the standard user locations `~/.local/share` and `~/.config`.
> You may want to change these values to some other path to separate container and host system data.
