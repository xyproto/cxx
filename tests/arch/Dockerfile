FROM base/devel

ENV PACKAGE_SERVER_1 mirror.neuf.no/archlinux
ENV PACKAGE_SERVER_2 arch-mirror.wtako.net

# Use package server 1 and 2
RUN echo 'Server = http://'"$PACKAGE_SERVER_1"'/$repo/os/$arch' >/etc/pacman.d/mirrorlist && echo 'Server = http://'"$PACKAGE_SERVER_2"'/$repo/os/$arch' >>/etc/pacman.d/mirrorlist

# Update and upgrade packages
RUN pacman -Syu --noconfirm

# Install dependencies
RUN pacman -S --noconfirm --needed base-devel expac figlet freeglut gcc-ada git glew gnupg gtk3 jshon make pacutils perl perl-data-dump perl-json perl-libwww perl-lwp-protocol-https perl-term-readline-gnu perl-term-ui ppl qt5 scons sdl2 sfml

# Set up a user, just for running makepkg as non-root (it complains otherwise)
RUN useradd -m -G wheel -s /bin/bash aur

# Set up a directory for building packages
RUN mkdir -p aur && chown aur aur

# Download, build and install trizen
ENV pkg trizen
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

RUN echo 'ALL ALL = (ALL) NOPASSWD: ALL' > /etc/sudoers

# Trust Nick Clifton, for installing mingw-w64
RUN yes | gpg --recv-keys 13FCEF89DD9E3C4F

# Trust Nick Clifton, for installing mingw-w64
RUN yes | sudo -u aur gpg --recv-keys 13FCEF89DD9E3C4F

# Download build and install mingw-w64-binutils osl cloog mingw-w64-headers mingw-w64-gcc-base and wingw-w64-gcc
RUN sudo -u aur trizen -S mingw-w64-binutils osl cloog mingw-w64-headers mingw-w64-gcc-base and wingw-w64-gcc

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Clean and build all examples
RUN sakemake/tests/build_all.sh

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test
