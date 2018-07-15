# Tiny Linux executable, written in C

## Requirements

* sstrip
* gcc
* dietlibc (and `/usr/bin/diet`)
* upx

Installing dependencies on Arch Linux:

    pacman -S --needed base-devel dietlibc upx

## Build instructions

    sm tiny

This will produce an executable that is only 1716 bytes large, for 64-bit x86.

This is smaller than the executable produced by `tcc -Os`, which is 1984 bytes after stripping with `sstrip`.
