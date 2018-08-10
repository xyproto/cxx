FROM base/devel

ENV PACKAGE_SERVER_1 mirror.neuf.no/archlinux
ENV PACKAGE_SERVER_2 arch-mirror.wtako.net
ENV PACKAGE_SERVER_3 mirrors.evowise.com/archlinux

# Use package server 1 and 2
RUN echo 'Server = http://'"$PACKAGE_SERVER_1"'/$repo/os/$arch' >/etc/pacman.d/mirrorlist
RUN echo 'Server = http://'"$PACKAGE_SERVER_2"'/$repo/os/$arch' >>/etc/pacman.d/mirrorlist
RUN echo 'Server = http://'"$PACKAGE_SERVER_3"'/$repo/os/$arch' >>/etc/pacman.d/mirrorlist

# Install required packages
RUN pacman -Syu --noconfirm --needed base-devel expac figlet freeglut git glew gnupg gtk3 go libconfig llvm ppl qt5 scons sdl2 sfml vulkan-devel

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

# Install mingw-w64-gcc. Using precompiled packages from Martchus. More likely to work than the AUR packages.
RUN echo -e '[ownstuff]\nSigLevel = Optional TrustAll\nServer = http://martchus.no-ip.biz/repo/arch/$repo/os/$arch' >>/etc/pacman.conf
RUN pacman -Syu mingw-w64-gcc --noconfirm --needed

# Prepare to install mingw-w64-gcc
#RUN pacman -Syu --noconfirm --needed gcc-ada gd libpaper libsigsegv libsynctex libxaw libxpm poppler potrace run-parts setconf t1lib texlive-bin texlive-core zziplib

# Install isl from AUR (currently does not work)
#RUN sudo -u aur yay -S isl --noconfirm

# Install isl from a prebuilt package instead
#COPY isl20-0.20-1-x86_64.pkg.tar.xz /tmp
#RUN sudo pacman -U /tmp/isl20-0.20-1-x86_64.pkg.tar.xz --noconfirm && rm -f /tmp/isl20-0.20-1-x86_64.pkg.tar.xz

#RUN sudo -u aur yay -S --noconfirm cloog
#RUN sudo -u aur yay -S --noconfirm mingw-w64-headers-bootstrap
#RUN sudo -u aur yay -S --noconfirm mingw-w64-headers
#RUN sudo -u aur yay -S --noconfirm mingw-w64-binutils

# Download, build and install mingw-w64-gcc-base
#ENV pkg mingw-w64-gcc-base
#RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur setconf PKGBUILD _islver=0.20 && sudo -u aur makepkg --skippgpcheck
#RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Prepare to install mingw-w64-gcc
#RUN sudo -u aur yay -S --noconfirm mingw-w64-winpthreads
#RUN sudo -u aur yay -S --noconfirm mingw-w64-crt

# Download, build and install mingw-w64-gcc
#ENV pkg mingw-w64-gcc
#RUN pacman -S --noconfirm --needed setconf
#RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur setconf PKGBUILD _islver=0.20 && sudo -u aur makepkg --skippgpcheck
#RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

RUN pacman -S glfw glm openal --noconfirm

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    make -C sakemake install && cp -r sakemake/{tests,examples} . && rm -rf sakemake

# Build and run the hello_test in hello/common
RUN sm -C examples/hello/common test

# Clean and build all examples
RUN tests/build_all.sh
