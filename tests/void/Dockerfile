FROM voidlinux/voidlinux

# Update packages
RUN xbps-install -Su -y

# Install packages
RUN xbps-install -S -y SDL2-devel SFML-devel boost-devel figlet gcc git glew-devel gtk+3-devel libfreeglut-devel make pkg-config qt5-devel scons

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Clean and build all examples
RUN sakemake/tests/build_all.sh win64crate

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test
