#!/bin/sh

set -x

# Select a package mirror
echo 'ftp://ftp.netbsd.org/pub/pkgsrc/packages/NetBSD/amd64/7.1/All' | sudo tee /usr/pkg/etc/pkgin/repositories.conf

# pkgin -y is not needed for the update command
sudo pkgin update

## Install packages required for Sakemake and for building the examples
sudo pkgin -y install SDL2 SDL2_image SDL2_mixer SDL2_net SDL2_ttf bash docker freeglut gcc7 pkgin install git glew gmake gtk3+ pkgconf qt5 scons

# Clone or pull sakemake
test -d sakemake && (cd sakemake; git -c http.sslVerify=false pull origin master) || git -c http.sslVerify=false clone 'https://github.com/xyproto/sakemake'

# Install Sakemake
gmake -C sakemake install
