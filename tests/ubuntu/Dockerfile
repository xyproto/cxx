FROM ubuntu:18.10

# Update and install packages
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get upgrade && \
    apt-get install -y -q build-essential figlet freeglut3-dev freeglut3-dev g++-mingw-w64-x86-64 git gtk+3-dev libboost-dev libboost-all-dev libboost-filesystem-dev libglew-dev libsdl2-dev libsfml-dev make mesa-common-dev qt5-default qtdeclarative5-dev scons python3 && \
    apt-get clean

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test

# Clean and build all examples
RUN sakemake/tests/all.py

