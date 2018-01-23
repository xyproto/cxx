#!/bin/sh
#
# Remember to search for packages case insensitively, with "sudo pkg search -i asdf"
#

# Update package repo
pkg update -f

# Upgrade packages
pkg upgrade -y

# Install packages required for Sakemake and for building the examples
pkg install -y bash figlet freeglut gcc7 git glew gmake gtk3 pkgconf qt5 scons sdl2 sfml

# Setup mingw32-w64 (looks like it requires ports to be set up first)
#git clone https://github.com/takumin/ports-mingw-w64.git
#(cd ports-mingw-w64/devel/mingw64-gcc; make install clean)

# Setup docker
#pkg install -y ca_root_nss docker-freebsd
#kldload zfs
#dd if=/dev/zero of=/usr/local/dockerfs bs=1024K count=1000
#zpool create -f zroot /usr/local/dockerfs
#zfs create -o mountpoint=/usr/docker zroot/docker
#sysrc -f /etc/rc.conf docker_enable="YES"
#service docker start

# Clone and install Sakemake
rm -rf sakemake || true
git clone https://github.com/xyproto/sakemake
gmake -C sakemake install
