FROM voidlinux/voidlinux

# Update packages
RUN xbps-install -Su -y

# Install packages that usually install just fine
RUN xbps-install -S -y SDL2 gcc git glew-devel libfreeglut-devel make pkg-config scons boost-devel figlet

# Install packages that may fail
#RUN xbps-install -S -y gtk+3-devel qt5-devel
#RUN xbps-install -S -y SDL2-devel SFML-devel

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Clean and build all examples
RUN sakemake/tests/build_all.sh win64crate

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test
