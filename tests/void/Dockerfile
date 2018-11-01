FROM voidlinux/voidlinux
RUN xbps-install -v -Syu && xbps-install -v -Sy SDL2-devel

#git make gcc

#RUN xbps-install -Sy scons boost-devel figlet python3 libopenal-devel libconfig++-devel SDL2-devel SFML-devel make gcc git

# Install packages that usually install just fine
#RUN xbps-install -Sy glew-devel libfreeglut-devel pkg-config

#RUN xbps-install -S -y SDL2-devel SDL2_mixer-devel qt5-devel gtk+3-devel

# Install sakemake, but don't keep the git checkout in the docker image
#RUN git clone https://github.com/xyproto/sakemake && \
#    cd sakemake && \
#    make install
#
## Build and run the hello_test in hello/common
#RUN sm -C sakemake/examples/hello/common test
#
## Clean and build some of the examples
#CMD sakemake/tests/all.py fastclean:build gtk3 qt5 sdl2 sdl2_opengl sfml win64crate 
