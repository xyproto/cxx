# snakemake

Opinionated build system that uses Python (Python2 in Scons) together with Make for compiling C++17 code

## Usage

In a directory with C++17 source files ending with `.cpp`, and a `main.cpp` file, just:

    snakemake

Build and run tests:

    snakemake test

Clean:

    snakemake clean

Build with clang instead of gcc:

    snakemake clang

Debug build:

    snakemake debug

## Requirements

* Scons
* Make

## Installation

With your distro package manager, or with sudo:

`sudo make install`

In a package:

`make PREFIX="$pkgdir" install`

## Uninstallation

`sudo make uninstall`

## Opinionated opinions

* Include files are expected to be found in `../include`.
* Common `.cpp` files (the corresponding code to header files in ../include) are expected to be found in `../common`.
* Tests are expected to end with `_test.cpp` and will be ignored when building `main.cpp`.
