# Flask-Socket Stream vs WebRTC Stream
A simple demo to compare the performance between socket and webrtc ( rtsp )

# Demo
Flask-socket provide a lower speed when streaming, and WebRTC will delay for a second because the buffer must be collected at first.
* GIF ( 20 FPS )
    ![DEMO](./figures/socket-vs-webrtc.gif)
* Video - [flask-socket vs webrtc ( youtube )](https://youtu.be/jth1QB32Ask)

# How to run
```bash
# Build Docker Image
./docker/build.sh

# Run WebRTC Server Container
./webrtc.sh

# Run Flask App
./docker/run.sh ./gu-run.sh
```

# Licence
Thanks to [deepch](https://github.com/deepch) provide a perfect golang project ( [RTSPtoWeb](https://github.com/deepch/RTSPtoWeb) ).


