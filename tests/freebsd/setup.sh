#!/bin/sh
#
# Remember to search for packages case insensitively, with "sudo pkg search -i asdf"
#

# Update package repo
sudo pkg update -f

# Upgrade packages
sudo pkg upgrade -y

# Install packages required for Sakemake and for building the examples
sudo pkg install -y bash figlet freeglut gcc7 git glew gmake gtk3 mingw32-gcc pkgconf qt5 scons sdl2

# Clone and install Sakemake
git clone https://github.com/xyproto/sakemake
sudo gmake -C sakemake install
