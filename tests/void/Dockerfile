FROM voidlinux/voidlinux

# The update command must be run twice on Void Linux for being able to install SDL2-devel afterwards
RUN xbps-install -v -Syu && xbps-install -v -Syu

RUN xbps-install -v -Sy SDL2-devel SDL2_mixer-devel SFML-devel boost-devel figlet gcc git glew-devel gtk+3-devel libconfig++-devel libfreeglut-devel libopenal-devel make pkg-config python3 qt5-devel scons fcgi

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Clean and build almost all of the examples
CMD sakemake/tests/all.py fastclean:build config win64crate notify entityx pytorch
