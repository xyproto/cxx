#!/bin/sh
#
# Remember to search for packages case insensitively, with "sudo pkg search -i asdf"
#

# Update package repo
#pkg-static update -f

# Upgrade packages
#pkg-static upgrade -y

# Install basic packages for Linux-like development
pkg_add bash git gmake pkgconf python-3.6.8p0 scons

# Install packages required for CXX and for building the examples
pkg_add figlet freeglut gcc-8.3.0 g++-8.3.0 libconfig

#pkg_add glew glfw glm libconfig sdl2 sdl2_mixer

#vulkan-headers vulkan-tools
#pkg_add gtk3
#pkg_add qt5

# Setup mingw32-w64 (looks like it requires ports to be set up first)
#git clone https://github.com/takumin/ports-mingw-w64.git
#(cd ports-mingw-w64/devel/mingw64-gcc; make install clean)

# Setup docker
#pkg_add ca_root_nss docker-openbsd
#kldload zfs
#dd if=/dev/zero of=/usr/local/dockerfs bs=1024K count=1000
#zpool create -f zroot /usr/local/dockerfs
#zfs create -o mountpoint=/usr/docker zroot/docker
#sysrc -f /etc/rc.conf docker_enable="YES"
#service docker start

# Clone and install CXX
rm -rf cxx || true
git clone https://github.com/xyproto/cxx
gmake -C cxx install
