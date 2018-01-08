#!/bin/sh

# WIP, currently does not work

# Update package repo
pkgsrc update -f

# Upgrade packages
pkgsrc upgrade -y

# Install packages required for Sakemake and for building the examples
pkgsrc install -y bash figlet freeglut gcc7 git glew gmake gtk3 pkgconf qt5 scons sdl2

#pkgsrc install mingw32-w64

# Clone and install Sakemake
rm -rf sakemake || true
git clone https://github.com/xyproto/sakemake
gmake -C sakemake install
