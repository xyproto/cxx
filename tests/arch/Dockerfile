FROM base/devel

# Update and install packages
RUN pacman -Syu --noconfirm
RUN pacman -S --noconfirm --needed base-devel figlet freeglut git glew gtk3 make mingw-w64 qt5 scons sdl2

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Clean and build all examples
RUN sakemake/tests/build_all.sh

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test
