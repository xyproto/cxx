#!/bin/sh
sudo pkg install freeglut gcc7 git glew gmake gtk3 mingw32 pkgconf qt5 scons sdl20
git clone https://github.com/xyproto/sakemake
sudo gmake -C sakemake install
