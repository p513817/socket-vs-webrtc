#!/bin/bash
CMD=$1

docker run -it --rm \
--name simple-socket-stream \
--net=host --ipc=host \
--privileged -v /dev:/dev \
-v /tmp/.x11-unix:/tmp/.x11-unix:rw \
-e DISPLAY=unix${DISPLAY} \
-v $(pwd):/workspace \
simple-socket-stream "${CMD}"