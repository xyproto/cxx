FROM archlinux/base

ENV PACKAGE_SERVER_1 mirror.clarkson.edu/archlinux
ENV PACKAGE_SERVER_2 mirror.pointysoftware.net/archlinux
ENV PACKAGE_SERVER_3 mirror.ziemer.bz/archlinux

# Use these package servers, in prioritized order
RUN echo 'Server = http://'"$PACKAGE_SERVER_1"'/$repo/os/$arch' >/etc/pacman.d/mirrorlist
RUN echo 'Server = http://'"$PACKAGE_SERVER_2"'/$repo/os/$arch' >>/etc/pacman.d/mirrorlist
RUN echo 'Server = http://'"$PACKAGE_SERVER_3"'/$repo/os/$arch' >>/etc/pacman.d/mirrorlist

# Install required packages
RUN pacman -Syu --noconfirm --needed base-devel boost expac figlet freeglut git glew glfw glm gnupg go gtk3 libconfig llvm openal pkgfile ppl python qt5 scons sdl2 sdl2_mixer sfml vulkan-devel entityx python-pytorch

# Prepare to install mingw-w64-gcc, using precompiled packages from Martchus.
# More likely to work than the AUR packages.
RUN echo -e '[ownstuff]\nSigLevel = Optional TrustAll\nServer = http://martchus.no-ip.biz/repo/arch/$repo/os/$arch' >>/etc/pacman.conf

# Install cxx, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/cxx && \
    make -C cxx install && cp -r cxx/{tests,examples} . && rm -rf cxx

# Build and run the hello_test in hello/common
RUN cxx -C cxx/examples/hello/common test

# Install mingw-w64-gcc. If it works out, run all tests. If not, run all tests except win64crate
CMD pacman -Syu mingw-w64-gcc --noconfirm --needed && test/all.py || tests/all.py win64crate
