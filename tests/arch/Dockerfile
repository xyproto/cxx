FROM base/devel

# Update and install packages
RUN pacman -Syu --noconfirm
RUN pacman -S --noconfirm --needed base-devel figlet freeglut git glew gtk3 make qt5 scons sdl2 sfml

# Set up a user, just for running makepkg as non-root (it complains otherwise)
RUN useradd -m -G wheel -s /bin/bash makepkg

# Install packer from AUR
RUN mkdir -p packer && cd packer && curl -sLo PKGBUILD 'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=packer' && sudo -u makepkg makepkg && pacman -U packer*.pkg.* --noconfirm

# Install mingw-w64-gcc and mingw-w64-sdl2
RUN packer -S mingw-w64-gcc mingw-w64-sdl2 --noconfirm

# Install sakemake, but don't keep the git checkout in the docker image
RUN git clone https://github.com/xyproto/sakemake && \
    cd sakemake && \
    make install

# Clean and build all examples
RUN sakemake/tests/build_all.sh

# Build and run the hello_test in hello/common
RUN sm -C sakemake/examples/hello/common test
