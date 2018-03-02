FROM base/devel

ENV PACKAGE_SERVER_1 mirror.neuf.no/archlinux
ENV PACKAGE_SERVER_2 arch-mirror.wtako.net

# Use package server 1 and 2
RUN echo 'Server = http://'"$PACKAGE_SERVER_1"'/$repo/os/$arch' >/etc/pacman.d/mirrorlist && echo 'Server = http://'"$PACKAGE_SERVER_2"'/$repo/os/$arch' >>/etc/pacman.d/mirrorlist

# Update and upgrade packages
RUN pacman -Syu --noconfirm

# Install dependencies
RUN pacman -S --noconfirm --needed base-devel expac figlet freeglut gcc-ada git glew gtk3 jshon make ppl qt5 scons sdl2 sfml

# Set up a user, just for running makepkg as non-root (it complains otherwise)
RUN useradd -m -G wheel -s /bin/bash aur

# Set up a directory for building packages
RUN mkdir -p aur && chown aur aur

# Download, build and install mingw-w64-binutils
ENV pkg mingw-w64-binutils
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Download, build and install isl
ENV pkg isl
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Download, build and install osl
ENV pkg osl
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Download, build and install cloog
ENV pkg cloog
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Download, build and install mingw-w64-headers
ENV pkg mingw-w64-headers
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck --skipchecksums
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Download, build and all mingw-w64-headers-bootstrap
ENV pkg mingw-w64-headers-bootstrap
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Download, build and all mingw-w64-gcc-base
ENV pkg mingw-w64-gcc-base
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Download, build and install mingw-w64-crt
ENV pkg mingw-w64-crt
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Download, build and install mingw-w64-winpthreads
ENV pkg mingw-w64-winpthreads
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN (yes | pacman -U aur/*.pkg.* --force) && rm aur/*.pkg.*

# Download, build and install mingw-w64-gcc
ENV pkg mingw-w64-gcc
RUN cd aur && sudo -u aur curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h='"$pkg" && sudo -u aur makepkg --skippgpcheck
RUN pacman -U aur/*.pkg.* --noconfirm && rm aur/*.pkg.*

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Clean and build all examples
RUN sakemake/tests/build_all.sh

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test
