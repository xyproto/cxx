FROM ubuntu:17.10

ENV TERM=dumb

# Update and install packages
RUN apt-get update && \
    apt-get upgrade && \
    apt-get install -y -q build-essential figlet git gtk+3-dev libsdl2-dev make scons && \
    apt-get clean

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Clean and build all examples
RUN sakemake/tests/build_all.sh

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test
