#!/bin/bash

docker run --rm -dt \
--name rtsp-to-web \
-v $(pwd)/webrtc.json:/config/config.json \
--network host \
ghcr.io/deepch/rtsptoweb:latest