FROM nvcr.io/nvidia/tensorrt:21.03-py3 as base

# Setup Time Zone
ARG TIMEZONE=Asia/Taipei
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=${TIMEZONE}

RUN apt-get update \
    && apt-get -y install tzdata \
    && ln -fs /usr/share/zoneinfo/${TIMEZONE} /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata

# Basic
RUN apt-get install -yq pkg-config yasm \
    python3-dev python3-pip python3-numpy \
    openssl libssl-dev  \
    wget curl unzip git vim \
    openssh-server  \
    libgtk2.0-dev libglib2.0-dev

# Gstreamer
RUN apt-get install -y libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-doc \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-pulseaudio \
    gir1.2-gst-rtsp-server-1.0

# Rebuild: OpenCV with ffmpeg and gst plugin
RUN apt-get install ffmpeg -y \
    && wget https://github.com/opencv/opencv/archive/4.5.3.zip \
    && unzip 4.5.3.zip && rm 4.5.3.zip \
    && mkdir ./opencv-4.5.3/build && cd ./opencv-4.5.3/build \
    && cmake -DCUDA_FAST_MATH=ON .. \
    && make -j"$(nproc)" \
    && make install

# Python Requirement
RUN pip3 install gobject pygobject \
    Flask==2.0.3 \
    Flask-Cors==3.0.10 \
    flask-sock \
    gunicorn==20.1.0 \
    python-dateutil==2.8.2 \
    flask_mqtt==1.1.1  \
    paho-mqtt==1.6.1 \
    colorlog \
    && apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall -y netbase

# Go Lang
RUN wget https://go.dev/dl/go1.19.1.linux-amd64.tar.gz \
    && rm -rf /usr/local/go \
    && tar -C /usr/local -xzf go1.19.1.linux-amd64.tar.gz

ENV PATH=$PATH:/usr/local/go/bin

WORKDIR /workspace
CMD bash