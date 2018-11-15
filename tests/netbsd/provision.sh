#!/bin/sh

set -x

#sudo pkg-unlock --all

# Select a package mirror. The version number here must be in sync with the
# Vagrant image that is used as a basis for this provisioning.
echo 'ftp://ftp.fr.netbsd.org/pub/pkgsrc/packages/NetBSD/amd64/7.0/All' | sudo tee /usr/pkg/etc/pkgin/repositories.conf

# pkgin -y is not needed for the update command, it only updates the database
sudo pkgin update

# install basic tools
sudo pkgin -y install bash git gmake pkgconf python37

# Install packages required for Sakemake and for building the examples
sudo pkgin -y install SDL2 SDL2_image SDL2_mixer SDL2_net SDL2_ttf docker freeglut gcc7 glew glm glut openal qt5 scons boost
# gtk3 libconfig sfml

# Clone or pull sakemake
test -d sakemake && (cd sakemake; git -c http.sslVerify=false pull origin master) || git -c http.sslVerify=false clone 'https://github.com/xyproto/sakemake'

# Fix permissions
chown -R vagrant:users .

# Install Sakemake
gmake -C sakemake install
