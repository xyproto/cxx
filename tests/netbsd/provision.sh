#!/bin/sh

set -v

echo 'ftp://ftp.netbsd.org/pub/pkgsrc/packages/NetBSD/amd64/7.1/All' | sudo tee /usr/pkg/etc/pkgin/repositories.conf

sudo pkgin update

## Install packages required for Sakemake and for building the examples
sudo pkgin -y install SDL2 SDL2_image SDL2_mixer SDL2_net SDL2_ttf bash docker freeglut gcc7 pkgin install git glew gmake gtk3+ pkgconf qt5 scons

# sudo pkgin -y install mozilla-rootcerts
# sudo mozilla-rootcerts install

# Setup mingw32-w64 (looks like it requires ports to be set up first)
#git clone https://github.com/takumin/ports-mingw-w64.git
#(cd ports-mingw-w64/devel/mingw64-gcc; make install clean)

# Clone and install Sakemake
rm -rf sakemake || true
#git clone https://github.com/xyproto/sakemake
git -c http.sslVerify=false clone https://github.com/xyproto/sakemake
gmake -C sakemake install
