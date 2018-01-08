#!/bin/sh
#
# Remember to search for packages case insensitively, with "sudo pkg search -i asdf"
#

# Update package repo
pkg update -f

# Upgrade packages
pkg upgrade -y

# Install packages required for Sakemake and for building the examples
pkg install -y bash docker figlet freeglut gcc7 git glew gmake gtk3 pkgconf qt5 scons sdl2

# Clone and install Sakemake
rm -rf sakemake || true
git clone https://github.com/xyproto/sakemake
gmake -C sakemake install
