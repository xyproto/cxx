FROM base/devel

ENV PACKAGE_SERVER_1 mirror.clarkson.edu/archlinux
ENV PACKAGE_SERVER_2 mirror.pointysoftware.net/archlinux
ENV PACKAGE_SERVER_3 mirror.ziemer.bz/archlinux

# Use these package servers, in prioritized order
RUN echo 'Server = http://'"$PACKAGE_SERVER_1"'/$repo/os/$arch' >/etc/pacman.d/mirrorlist
RUN echo 'Server = http://'"$PACKAGE_SERVER_2"'/$repo/os/$arch' >>/etc/pacman.d/mirrorlist
RUN echo 'Server = http://'"$PACKAGE_SERVER_3"'/$repo/os/$arch' >>/etc/pacman.d/mirrorlist

# Install required packages
RUN pacman -Syu --noconfirm --needed base-devel boost expac figlet freeglut git glew glfw glm gnupg go gtk3 libconfig llvm openal ppl qt5 scons sdl2 sfml vulkan-devel

# Install mingw-w64-gcc, using precompiled packages from Martchus. More likely to work than the AUR packages.
RUN echo -e '[ownstuff]\nSigLevel = Optional TrustAll\nServer = http://martchus.no-ip.biz/repo/arch/$repo/os/$arch' >>/etc/pacman.conf
RUN pacman -Syu mingw-w64-gcc --noconfirm --needed

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    make -C sakemake install && cp -r sakemake/{tests,examples} . && rm -rf sakemake

# Build and run the hello_test in hello/common
RUN sm -C examples/hello/common test

# Clean and build all examples
RUN tests/build_all.sh
