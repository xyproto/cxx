FROM base/devel

ENV PACKAGE_SERVER_1 mirror.neuf.no/archlinux
ENV PACKAGE_SERVER_2 arch-mirror.wtako.net
ENV PACKAGE_SERVER_3 mirrors.evowise.com/archlinux

# Use package server 1 and 2
RUN echo 'Server = http://'"$PACKAGE_SERVER_1"'/$repo/os/$arch' >/etc/pacman.d/mirrorlist
RUN echo 'Server = http://'"$PACKAGE_SERVER_2"'/$repo/os/$arch' >>/etc/pacman.d/mirrorlist
RUN echo 'Server = http://'"$PACKAGE_SERVER_3"'/$repo/os/$arch' >>/etc/pacman.d/mirrorlist

# Install required packages
RUN pacman -Syu --noconfirm --needed base-devel expac figlet freeglut git glew gnupg gtk3 go llvm ppl qt5 scons sdl2 sfml vulkan-devel

# Set up a user, just for running makepkg as non-root (it complains otherwise)
RUN useradd -m -G wheel -s /bin/bash aur

# Set up a directory for building packages
RUN mkdir -p aur && chown aur aur

# Download, build and install yay
ENV pkg yay
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Don't ask for a password when installing with sudo below
RUN echo 'ALL ALL = (ALL) NOPASSWD: ALL' > /etc/sudoers

# Trust Nick Clifton, for installing mingw-w64
RUN yes | gpg --keyserver keys2.kfwebs.net --recv-keys 13FCEF89DD9E3C4F
RUN yes | sudo -u aur gpg --keyserver keys2.kfwebs.net --recv-keys 13FCEF89DD9E3C4F
RUN yes | gpg --keyserver keys2.kfwebs.net --recv-keys 93BDB53CD4EBC740
RUN yes | sudo -u aur gpg --keyserver keys2.kfwebs.net --recv-keys 93BDB53CD4EBC740

# Install isl from AUR, using an alternative download URL
RUN mkdir -p /tmp/isl
RUN curl -Lo /tmp/isl/isl-0.20.tar.xz https://mirror.sobukus.de/files/src/isl/isl-0.20.tar.xz
RUN sudo -u aur yay --builddir /tmp -S isl --noconfirm

# Install mingw-w64-gcc from AUR
RUN sudo -u aur yay -S mingw-w64-gcc --noconfirm

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    make -C sakemake install && cp -r sakemake/{tests,examples} . && rm -rf sakemake

# Build and run the hello_test in hello/common
RUN sm -C examples/hello/common test

# Clean and build all examples
RUN tests/build_all.sh
