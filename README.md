# [🍶](https://github.com/xyproto/sakemake) Sakemake [![Build Status](https://travis-ci.org/xyproto/sakemake.svg?branch=master)](https://travis-ci.org/xyproto/sakemake) [![License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://raw.githubusercontent.com/xyproto/algernon/master/LICENSE) [![Buildsystem](https://img.shields.io/badge/buildsystem-config--free-brightgreen.svg)](https://github.com/xyproto/sakemake)

Configuration-free build system for Arch Linux, FreeBSD, Ubuntu 17.10 or macOS w/Homebrew, **for developers that just want to program in C++17 and build one or more executables** and not have to deal with build configuration and compilation flags. Defines for directories like `img` and `data` are provided. A simple way to test and package code is also provided.

Required libraries must still be installed manually.

*Sakemake* also provides a way to structure your C++17 code, test and debug your source files. It also makes it easy for Linux (or Homebrew) packagers to package your project, and for users to build and install it.

It uses scons, make and pkg-config under the hood, while providing a tool that aims to be as easy to use as `go build` for Go. *Sakemake* may be rewritten to not depend on these tools in the future.

Dependencies are discovered automatically, and the correct flags are given to the C++ compiler. If the dependencies are discovered correctly, the project is *Sakemake*-compliant and may display the badge below as a guarantee for users that the project will be easy to deal with.

**No build-configuration files are needed!** No `CMakeLists.txt`, `Makefile`, `SConstruct`, `configure`, `automake` or `Makefile.in`. Only a `make.cpp` file will work, but a *Sakemake*-compatible directory structure is recommended.

The latest versions of both GCC (g++) and Clang (clang++) are always supported, and the latest released C++ standard. Create an issue if there are problems.

If you are developing a C++ **library**, *Sakemake* is not for you, yet. If you are looking for a configuration-free build system for **executables**, on Linux, macOS or FreeBSD, *Sakemake* might be for you. *(The only way to be sure is to give it a spin)*.

`x86_64-w64-mingw32-g++` or a working installation of `docker` is required for compiling executables for 64-bit Windows. This docker image is used if the `x86_64-w64-mingw32-g++` executable is missing: `jhasse/mingw:2017-10-19`.

## Usage

In a directory with C++17 source files ending with `.cpp`, and a `main.cpp` file, building is as simple as:

    sm

#### Build and run:

    sm run

#### Build and run tests in a directory with files ending with `_test.cpp`:

    sm test

#### Clean:

    sm clean

#### Build with clang instead of gcc:

    sm clang

#### Debug build:

    sm debug

#### Building a specific directory (`sm` can take the same flags as `make`):

    sm -C examples/hello

#### Cleaning and building:

    sm rebuild

#### Installing on the local system, using sudo:

    sudo PREFIX=/usr sm install

The name of the current directory will be used as the executable name.

#### Packaging a project into $pkgdir (`pkg` by default):

    DESTDIR="$pkgdir" PREFIX=/usr sm install

--- or just ---

    sm pkg

The name of the current directory will be used as the executable name.

#### Build a smaller executable:

    sm small

#### Strict compilation flags (complains about all things):

    sm strict

#### Sloppy compilation flags (will ignore all warnings):

    sm sloppy

#### Get the current version:

    sm version

#### Format the source code:

    sm fmt

#### Generate a qmake / QtCreator project file:

    sm pro

Tested with QtCreator 4.6 on Arch Linux.

## Features and limitations

* **No configuration files are needed**, as long as the *Sakemake* directory structure is followed.
* **Auto-detection** of include, define and library flags, based on which files are included from `/usr/include`, using **`pkg-config`**. It also uses system-specific ways of attempting to detect which packages provides which compilation flags. Not all libraries, include files and cxxflags can be auto-detected yet, but more are to be added.
* Built-in support for testing, clang, debug builds and only rebuilding files that needs to be rebuilt.
* Uses the caching that is supplied by SCons, no ccache is needed.
* Does not use a `build` directory, it's okay that the `main` executable ends up in the root folder of the project. `main.cpp` can be placed in the root folder of the project, or in its own directory.
* Only tested on Linux, FreeBSD and macOS. Should be easy to port to other systems that also has a package manager and pkg-config (or equivalent way to discover build flags).
* Your include files are expected to be found in `./include` or `../include`.
* Source files used by multiple executables in your project are expected to be placed in `./common` or `../common`.
* Tests are expected to end with `_test.cpp` and will be ignored when building `main.cpp`.
* See the `hello` example in the `examples` directory for the suggested directory structure.
* For now, *Sakemake* is only meant to be able to build executables, not libraries.
* The dependency discovery is reasonably fast, the compilation itself still takes the longest. Not to speak of the time it can take to discover build flags for some C++ libraries and features manually.

## Suggested directory structure

For a "Hello, World!" program that places the text-generation in a `string hello()` function, this is one way to structure the files:


```
.
├── hello/main.cpp
├── hello/include/hello.h
├── hello/include/test.h
├── hello/common/hello.cpp
└── hello/common/hello_test.cpp
```

#### --- or if you prefer one directory per executable ---

```
.
└── hello/hello1/main.cpp
└── hello/hello2/main.cpp
└── hello/include/hello.h
└── hello/include/test.h
└── hello/common/hello.cpp
└── hello/common/hello_test.cpp
```

**main.cpp**

```c++
#include <iostream>
#include "hello.h"

int main()
{
    std::cout << hello() << std::endl;
    return 0;
}
```

**hello.h**

```c++
#pragma once

#include <string>

std::string hello();
```

**hello.cpp**

```c++
#include "hello.h"

using namespace std::literals;

std::string hello()
{
    return "Hello, World!"s;
}
```

**hello_test.cpp**

```c++
#include "test.h"
#include "hello.h"

using namespace std::literals;

void hello_test()
{
    equal(hello(), "Hello, World!"s);
}

int main()
{
    hello_test();
    return 0;
}
```

**test.h**

```c++
#pragma once

#include <iostream>
#include <cstdlib>

template<typename T>
void equal(T a, T b)
{
    if (a == b) {
      std::cout << "YES" << std::endl;
    } else {
      std::cerr << "NO" << std::endl;
      exit(EXIT_FAILURE);
    }
}
```

## Requirements

* `scons`
* `make`
* `pkg-config`
* `g++` with support for c++17 (gcc version 7.2 or higher should work)
* `lldb` or `gdb` for debugging

#### Optional requirements

* `clang++` with support for C++17 (build with `sm clang`).
* `pkgfile` on Arch Linux, for faster dependency discovery.
* `apt-file` on Debian/Ubuntu, for faster dependency discovery.
* `x86_64-w64-mingw32-g++` or `docker`, for cross-compiling executables for 64-bit Windows.
* `wine`, for testing executables compiled for 64-bit Windows (`sm run`).
* `valgrind`, for profiling (`sm valgrind`).
* `kcachegrind`, for viewing the information produced by *valgrind*.
* `gprof2dot` and `dot`, for producing a graph from the information produced by valgrind.
* `vagrant`, for testing *sakemake* on other operating systems.
* `figlet`, for nicer output when running the `tests/build_all.sh` script, for building all the examples.
* Development packages for `SDL2`, `OpenGL`, `glut`, `glfw`, `sfml`, `GTK+3` and `Qt5`, for building and running the examples.
* `x86_64-w64-mingw32-g++` or `docker` is needed for building the `win64crate` example.
* `clang-format` for `sm fmt`.

## Defines

These defines are passed to the compiler, if the corresponding paths exist (or will exist, when packaging):

* `DATADIR` is defined as `./data` or `../data` (when developing) and `$PREFIX/share/application_name/data` (at installation time)
* `IMGDIR` is defined as `./img` or `../img` (when developing) and `$PREFIX/share/application_name/img` (at installation time)
* `SHADERDIR` is defined as `./shaders` or `../shaders` (when developing) and `$PREFIX/share/application_name/shaders` (at installation time)
* `SHAREDIR` is defined as `./share` or `../share` (when developing) and `$PREFIX/share/application_name` (at installation time)
* `RESOURCEDIR` is defined as `./resources` or `../resources` (when developing) and `$PREFIX/share/application_name/resources` (at installation time)

This makes it easy to have an `img`, `data` or `resources` directory where files can be found and used both at development and at installation-time.

See `examples/sdl2` and `examples/win64crate` for examples that uses `IMGDIR`.

See `examples/mixer` for an example that uses `RESOURCEDIR`.

An alternative method to using defines (defined with `-D` when building) is to use something like `SDL_GetBasePath()`. Example: [res_path.h](https://github.com/libSDL2pp/TwinklebearDev-Lessons-libSDL2pp/blob/sdl2pp/include/res_path.h).

## C++17 on macOS

For installing a recent enough version of C++ on macOS, installing gcc 7 with `brew` is one possible approach:

    brew install gcc@7

The other requirements can be installed with:

    brew install scons make pkg-config

## C++17 on Arch Linux

g++ with support for C++17 should already be installed.

Install scons and base-devel, if needed:

    pacman -S scons base-devel --needed

## C++17 on Debian or Ubuntu

Ubuntu 17.10 has C++17 support by default. For older versions of Ubuntu or Debian, you might need to install GCC 7 from the testing repository, or from a PPA.

Install build-essential, scons and pkg-config:

    apt install build-essential scons pkg-config

## C++17 on FreeBSD

FreeBSD 11.1 comes with C++17 support, but you may wish to install gcc7 or later.

Install pkg-conf, scons and gmake:

    pkg install pkgconf scons gmake

## Installation

Manual installation with `make` and `sudo`:

`sudo make install`

On FreeBSD, use `gmake` instead of `make`.

If possible, install *Sakemake* with the package manager that comes with your OS/distro instead.

## Uninstallation

`sudo make uninstall`

## Convention over configuration

## The "Configuration-Free Manifesto"

> Convention over configuration

Rules for Configuration-free projects:

#### Filenames

* All include filenames should contain no spaces or special characters (a-z, A-Z, 0-9) and end with `.h` or `.hpp`.
* All C++17 source filenames should contain no spaces or special characters (a-z, A-Z, 0-9) and end with `.cpp`, `.cc` or `.cxx`.
* The main source file could be named `main.cpp` or `main.cc`, but it does not have to.
* Files ending with `_test.*` are special, and will not be used when compiling the main executable(s).

#### Directories

* `include/` should contain all include files belonging to the project.
* `common/` should contain all source code that can be shared between multiple executables.
* The top level directory, or `src/`, or a custom directory should contain at least one source file containing a `main` function.
* The name of the produced executable will be the same as the name of the parent directory, or `main` if the parent directory is `src`.
* `img/` should contain all images.
* `shaders/` should contain all shaders.
* `data/` should contain all other data files needed by the program.
* `shared/` should contain all files optionally needed by the program, like example data.

#### Testing

* All source files, except the one containing the `main` function, should have a corresponding `_test` file. For instance: `quaternions.cc` and `quaternions_test.cc`.
* When running `sm test`, the `_test.*` files will be compiled and run.
* `*_test.*` files must each contain a `main` function.

#### CMake

* Projects that uses CMake (and need no extra command line arguments when running `cmake`) are also Sakemake compatible and can be built with:

    sm cmake

* Or if using CMake + Ninja:

    sm ninja

Only building projects with CMake is supported; not clearing, installing and packaging files.

## Source code formatting

* `sm fmt` will format C++17 source code in a single, fixed, formatting style (clang-format "Webkit"-style), which is not configurable, on purpose. Using `sm fmt` is optional.

## Feedback

The dream is that every executable and project written in C++17 should be able to build with `sakemake` on a modern Linux distro, FreeBSD or macOS system (with Homebrew), without any additional configuration.

If you have a project written in C++17 that you think should build with `sakemake`, but doesn't, please create an issue and include a link to your repository.

## Shields and images

### Shield

[![Buildsystem](https://img.shields.io/badge/buildsystem-config--free-brightgreen.svg)](https://github.com/xyproto/sakemake)

    [![Buildsystem](https://img.shields.io/badge/buildsystem-config--free-brightgreen.svg)](https://github.com/xyproto/sakemake)

### Award-style image

[![configuration-free](https://raw.githubusercontent.com/xyproto/sakemake/master/img/configuration_free_72.png)](https://github.com/xyproto/sakemake)

    [![configuration-free](https://raw.githubusercontent.com/xyproto/sakemake/master/img/configuration_free_72.png)](https://github.com/xyproto/sakemake)

### Emoji

[🍶](https://github.com/xyproto/sakemake)

    [🍶](https://github.com/xyproto/sakemake)

## Other projects that builds with Sakemake

* [glskeleton](https://github.com/xyproto/glskeleton), OpenGL shader example application, uses `glfw`, `glew` and `glm`.
* [vulkan_minimal_compute](https://github.com/xyproto/vulkan_minimal_compute), uses Vulkan for computations on the GPU.

## Editor configuration

If using syntastic and ViM, it may complain about defines that are supplied at build-time. Here is one way to silence the errors.

Adjust your ViM preferences:

    let g:syntastic_quiet_messages = {
        \ "!level": "errors",
        \ "regex":  [ 'RESOURCEDIR', 'DATADIR', 'IMGDIR', 'SHADERDIR', 'expected .*).* before string constant' ] }

## General info

* Version: 1.6.0
* License: MIT
* Author: Alexander F Rødseth &lt;xyproto@archlinux.org&gt;
