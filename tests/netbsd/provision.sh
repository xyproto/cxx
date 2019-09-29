#!/bin/sh

set -x

#sudo pkg-unlock --all

# Select a package mirror. The version number here must be in sync with the
# Vagrant image that is used as a basis for this provisioning.
echo 'ftp://ftp.fr.netbsd.org/pub/pkgsrc/packages/NetBSD/amd64/8.1/All' | sudo tee /usr/pkg/etc/pkgin/repositories.conf

# pkgin -y is not needed for the update command, it only updates the database
sudo pkgin update

# install basic tools
sudo pkgin -y install bash git gmake pkgconf python37

# Install packages required for CXX and for building the examples
sudo pkgin -y install SDL2 SDL2_image SDL2_mixer SDL2_net SDL2_ttf docker freeglut gcc8 glew glm glut openal qt5 py37-scons boost fcgi
# gtk3 libconfig sfml

# Clone or pull cxx
test -d cxx && (cd cxx; git -c http.sslVerify=false pull origin master) || git -c http.sslVerify=false clone 'https://github.com/xyproto/cxx'

# Fix permissions
#chown -R vagrant:users .

# Install CXX
gmake -C cxx install
