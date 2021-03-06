FROM debian:latest

RUN apt-get update && apt-get install -y \
    python \
    make \
    g++ \
    # WebKit
    git \
    ruby \
    flex \
    # Libraries
    # ALSA
    libasound2-dev \
    # CUPS
    libcups2-dev \
    # FontConfig
    libfontconfig1-dev \
    # Glib
    libglib2.0-dev \
    # GStreamer
    libgstreamer0.10-dev \
    libgstreamer-plugins-base1.0-dev \
    # GTK theme
    libgtk2.0-dev \
    # mtdev
    libmtdev-dev \
    # Networking/libproxy
    libproxy-dev \
    # Networking/OpenSSL
    libssl-dev \
    # Logging backends/journald
    libsystemd-journal-dev \
    # OpenGL / OpenVG
    libegl1-mesa-dev \
    libgl1-mesa-dev \
    libopenvg1-mesa-dev \
    # pkg-config
    pkg-config \
    # PulseAudio
    libpulse-dev \
    # xcb
    libxcb1-dev \
    libx11-xcb-dev \
    libxcb-keysyms1-dev \
    libxcb-image0-dev \
    libxcb-shm0-dev \
    libxcb-icccm4-dev \
    libxcb-sync-dev \
    libxcb-xfixes0-dev \
    libxrender-dev \
    libxcb-shape0-dev \
    libxcb-randr0-dev \
    libxcb-render-util0-dev \
    libxcb-glx0-dev \
    libxcb-xinerama0-dev \
    libxcb-xkb-dev \
    # udev
    libudev-dev \
    # xkbcommon-x11
    libxkbcommon-x11-dev \
    # xkbcommon-evdev
    libxkbcommon-dev \
    # qtwebengine
    gperf \
    snappy \
    bison \
    libxtst-dev \
    libdbus-1-dev \
    libpci-dev \
    libcap-dev \
    libxss-dev \
&& rm -rf /var/lib/apt/lists/*

VOLUME /data
WORKDIR /data
CMD ["/bin/bash"]
