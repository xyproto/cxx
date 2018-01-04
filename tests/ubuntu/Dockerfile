FROM ubuntu:17.10

# Update and install packages
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get upgrade && \
    apt-get install -y -q build-essential figlet git gtk+3-dev libsdl2-dev make scons freeglut3-dev mesa-common-dev qt5-default qtdeclarative5-dev g++-mingw-w64-x86-64 libglew-dev freeglut3-dev && \
    apt-get clean

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Clean and build all examples
RUN sakemake/tests/build_all.sh

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test

CMD ["/usr/bin/sm"]
