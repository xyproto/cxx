FROM voidlinux/voidlinux

# Update packages
RUN xbps-install -Su -y

# Install packages that usually install just fine
RUN xbps-install -S -y gcc git glew-devel libfreeglut-devel make pkg-config scons boost-devel figlet python3 libopenal-devel libconfig++-devel

#RUN xbps-install -S -y SDL2-devel SDL2_mixer-devel qt5-devel gtk+3-devel SFML-devel

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test

# Clean and build some of the examples
CMD sakemake/tests/all.py fastclean:build gtk3 qt5 sdl2 sdl2_opengl sfml win64crate 
