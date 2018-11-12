#!/bin/sh
#
# Remember to search for packages case insensitively, with "sudo pkg search -i asdf"
#

# Update package repo
pkg-static update -f

# Upgrade packages
pkg-static upgrade -y

# Install basic packages for Linux-like development
pkg install -y bash git gmake pkgconf python3

# Install packages required for Sakemake and for building the examples
pkg install -y figlet freeglut gcc8 glew glfw glm gtk3 libconfig qt5 scons sdl2

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
