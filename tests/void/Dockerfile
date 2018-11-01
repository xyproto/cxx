FROM voidlinux/voidlinux

# The update command must be run twice on Void Linux...
RUN xbps-install -v -Syu && xbps-install -v -Syu

RUN xbps-install -v -Sy SDL2-devel
RUN xbps-install -v -Sy scons boost-devel figlet python3 libopenal-devel libconfig++-devel SDL2-devel SFML-devel make gcc git
RUN xbps-install -v -Sy glew-devel libfreeglut-devel pkg-config
RUN xbps-install -v -Sy SDL2_mixer-devel qt5-devel gtk+3-devel

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test

# Clean and build some of the examples
#CMD sakemake/tests/all.py fastclean:build win64crate
CMD sakemake/tests/all.py fastclean:build gtk3 qt5 sdl2 sdl2_opengl sfml win64crate
