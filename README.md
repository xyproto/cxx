# CXX

[![Standard](https://img.shields.io/badge/C%2B%2B-23-blue.svg)](https://en.wikipedia.org/wiki/C%2B%2B#Standardization) [![License](https://img.shields.io/badge/license-BSD3-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Make modern C++ easier to deal with.

Have you ever had a single `main.cpp` file that you just want to compile, without any hassle?

`cxx` may fit your use case, provided you have all required libraries installed.

Using `cxx` is simple:

* `cxx` builds a project
* `cxx fmt` formats the source code
* `cxx debug` performs a debug build
* `cxx cmake` generates a `CMakeLists.txt` file that is compatible with many IDEs.
* `cxx pro` generates a project file that is compatible with QtCreator.
* `cxx cmake ninja` generates a `CMakeLists.txt` file and then builds the project using `ninja` (and `ccache`, if available).
* `cxx ninja` just builds the project using a `CMakeLists.txt` file and `ninja` (and `ccache`, if available).

No configuration files are needed, but the projects needs to either be very simple (a single `main.cpp`) or have a `cxx`-friendly directory structure.

The auto-detection of external libraries and headers relies on them being included in the main source file.

Tested on Arch Linux, FreeBSD, Ubuntu, macOS w/Homebrew, Void Linux and NetBSD. Docker images and Vagrant configuration files are available in the `tests` directory. Please submit a pull request if you have improvements for your platform!

Several examples are included in the `examples` directory. These mostly center around everything you would need to create a game in C++23: OpenGL, SDL2, Vulkan, Audio etc, but also includes examples for Gtk3, Qt5, X11 and Windows (the example should build and run on Linux, using `wine`).

The target audience is programmers that don't want to fiddle with makefiles, CMake etc, but want to either try out a feature in C++23, learn modern C++ or create a demoscene demo or a game.

As much as possible is auto-detected. As long as the right packages are installed, and includes are specified in the main source file, all dependencies, libraries and build flags should be handled automatically.

CXX provides a way to structure your C++ code, test and debug your source files. It also makes it easy for Linux (or Homebrew) packagers to package your project, and for users to build and install it.

If you're a long time C or C++ user and wish to write and distribute a C++ library, plain CMake might be a better fit.

## Packaging status

[![Packaging status](https://repology.org/badge/vertical-allrepos/cxx.svg)](https://repology.org/project/cxx/versions)

## Installation

If `cxx` is available by using your favorite package manager, that's usually the best way.

### Manual installation

First install CXX, so that `cxx` is in the path. Here is one way, using `git clone`, GNU Make and `sudo`:

    git clone https://github.com/xyproto/cxx
    cd cxx
    make && sudo make install

### Debian-based distros

For Debian or Ubuntu, these dependencies are recommended, for building CXX and most of the examples:

    build-essential figlet freeglut3-dev g++-mingw-w64-x86-64 git gtk+3-dev libboost-all-dev libc-dev libglew-dev libglibmm-2.4-dev libsdl2-dev libsfml-dev make mesa-common-dev qtbase5-dev qt5-default qtdeclarative5-dev scons python3 apt-utils apt-file libconfig++-dev libconfig++ libopenal-dev libglfw3-dev libvulkan-dev libglm-dev libsdl2-mixer-dev libboost-system-dev libfcgi-dev

### FreeBSD

For FreeBSD, here is one way of installing only the basic dependencies and CXX:

    pkg install -y bash git gmake pkgconf python3 scons
    git clone https://github.com/xyproto/cxx
    gmake -C cxx

Then as root:

    gmake -C cxx install

### NetBSD

One way of installing CXX and also the libraries needed by most of the example projects:

    pkgin -y install bash git gmake pkgconf python37 SDL2 SDL2_image SDL2_mixer SDL2_net SDL2_ttf docker freeglut gcc7 glew glm glut openal qt5 scons boost fcgi
    test -d cxx && (cd cxx; git -c http.sslVerify=false pull origin main) || git -c http.sslVerify=false clone 'https://github.com/xyproto/cxx'
    gmake -C cxx install

### Void Linux

Installing CXX and the libraries needed by most of the example projects:

    xbps-install -v -Sy SDL2-devel SDL2_mixer-devel SFML-devel boost-devel figlet gcc git glew-devel gtk+3-devel libconfig++-devel libfreeglut-devel libopenal-devel make pkg-config python3 qt5-devel scons fcgi
    git clone https://github.com/xyproto/cxx && cd cxx && make install

### Arch Linux

Just install `cxx` from AUR.

## Example Use

### Try out CXX and a small program that uses features from C++20

Create a **main.cpp** file:

```c++
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <ostream>
#include <string>

using namespace std::string_literals;

class Point {
public:
    double x;
    double y;
    double z;
};

std::ostream& operator<<(std::ostream& output, const Point& p)
{
    using std::setfill;
    using std::setw;
    output << "{ "s << setfill(' ') << setw(3) << p.x << ", "s << setfill(' ') << setw(3) << p.y
           << ", "s << setfill(' ') << setw(3) << p.z << " }"s;
    return output;
}

Point operator+(const Point& a, const Point& b)
{
    return Point { .x = a.x + b.x, .y = a.y + b.y, .z = a.z + b.z };
}

Point operator*(const Point& a, const Point& b)
{
    return Point { .x = a.x * b.x, .y = a.y * b.y, .z = a.z * b.z };
}

int main(int argc, char** argv)
{
    // designated initializers
    Point p1 { .x = 1, .y = 2, .z = 3 };
    Point p2 { .y = 42 };

    using std::cout;
    using std::endl;

    cout << "     p1 = " << p1 << endl;
    cout << "     p2 = " << p2 << endl;
    cout << "p1 + p2 = " << p1 + p2 << endl;
    cout << "p1 * p2 = " << p1 * p2 << endl;

    return EXIT_SUCCESS;
}
```

Then build the project with just:

    cxx

Rebuilding can be done with:

    cxx rebuild

While building and running can be done with:

    cxx run

If you wish to optimize the program, running it in a way that also records profiling information can be done with:

    cxx rec

The next time the project is built, the profiling information is used to optimize the program further:

    cxx

## Other commands

#### Building files ending with `_test.cpp`, then running them

    cxx test

#### Cleaning

    cxx clean

#### Building with `clang++` instead of `g++`:

    cxx clang

#### Building a specific directory

    cxx -C examples/hello

#### Installing on the local system, using sudo:

    sudo PREFIX=/usr cxx install

Either `main.cpp` or the C++ source files in the current directory will be used when building with `cxx`.

#### Packaging a project into `$pkgdir`:

    DESTDIR="$pkgdir" PREFIX=/usr cxx install

#### Packaging a project into a directory named `pkg`:

    cxx pkg

#### Build a small executable:

    cxx small

#### Build an executable with optimization flags turned on:

    cxx opt

#### Strict compilation flags (complains about all things):

    cxx strict

#### Sloppy compilation flags (will ignore all warnings):

    cxx sloppy

#### Get the current version:

    cxx version

## Directories

* The top level directory, or `src/`, or a custom directory can contain at least one source file containing a `main` function.
* The name of the produced executable will be the same as the name of the parent directory, or `main` if the parent directory is `src`.
* `include/` can contain all include files belonging to the project.
* `common/` can contain all source code that can be shared between multiple executables.
* `img/` can contain images.
* `shaders/` can contain shaders.
* `data/` can contain all other data files needed by the program.
* `shared/` can contain all files optionally needed by the program, like example data.

## Testing

* All source files, except the one containing the `main` function, can have a corresponding `_test` file. For instance: `quaternions.cc` and `quaternions_test.cc`.
* When running `cxx test`, the `_test.*` files will be compiled and run.
* `*_test.*` files must each contain a `main` function.

## Defines

These defines are passed to the compiler, if the corresponding paths exist (or will exist, when packaging):

* `DATADIR` is defined as `./data` or `../data` (when developing) and `$PREFIX/share/application_name/data` (at installation time)
* `IMGDIR` is defined as `./img` or `../img` (when developing) and `$PREFIX/share/application_name/img` (at installation time)
* `SHADERDIR` is defined as `./shaders` or `../shaders` (when developing) and `$PREFIX/share/application_name/shaders` (at installation time)
* `SHAREDIR` is defined as `./share` or `../share` (when developing) and `$PREFIX/share/application_name` (at installation time)
* `RESOURCEDIR` is defined as `./resources` or `../resources` (when developing) and `$PREFIX/share/application_name/resources` (at installation time)
* `RESDIR` is defined as `./res` or `../res` (when developing) and `$PREFIX/share/application_name/res` (at installation time)

(`application_name` is just an example).

This makes it easy to have an `img`, `data` or `resources` directory where files can be found and used both at development and at installation-time.

See `examples/sdl2` and `examples/win64crate` for examples that uses `IMGDIR`.

See `examples/mixer` for an example that uses `RESOURCEDIR`.

An alternative method to using defines (defined with `-D` when building) is to use something like `SDL_GetBasePath()`. Example: [`res_path.h`](https://github.com/libSDL2pp/TwinklebearDev-Lessons-libSDL2pp/blob/sdl2pp/include/res_path.h).

## Features and limitations

* **No configuration files are needed**, as long as the *CXX* directory structure is followed.
* **Auto-detection** of include, define and library flags, based on which files are included from `/usr/include`, using **`pkg-config`**. It also uses system-specific ways of attempting to detect which packages provides which compilation flags. Not all libraries, include files and cxxflags can be auto-detected yet, but more are to be added.
* Built-in support for testing, clang, debug builds and only rebuilding files that needs to be rebuilt.
* Does not use a `build` directory, it's okay that the `main` executable ends up in the root folder of the project. `main.cpp` can be placed in the root folder of the project, or in its own directory.
* Should be easy to port to other systems that also has a package manager and pkg-config (or equivalent way to discover build flags).
* Your include files are expected to be found in `./include` or `../include`.
* Source files used by multiple executables in your project are expected to be placed in `./common` or `../common`.
* Tests are expected to end with `_test.cpp` and will be ignored when building `main.cpp`.
* See the `hello` example in the `examples` directory for the suggested directory structure.
* For now, *CXX* is only meant to be able to build executables, not libraries.
* The dependency discovery is reasonably fast, the compilation itself still takes the longest time. Not to speak of the time it can take to discover build flags for some C++ libraries and features manually.
* For now, the generated `CMakeLists.txt` file is only meant to be used on the system it was generated on, not shipped for many different systems.

## Suggested directory structure

For a "Hello, World!" program that places the text-generation in a `string hello()` function, this is one way to structure the files, for separating the code into easily testable source files:


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
* `g++` with support for `-std=c++2b`.
* `pkg-config`, for systems where pkg-config is available

#### Optional requirements

* `clang++` with support for `-std=c++2b` (build with `cxx clang`).
* `lldb` or `gdb` for debugging
* `pkgfile` on Arch Linux, for faster dependency discovery.
* `apt-file` on Debian/Ubuntu, for faster dependency discovery.
* `x86_64-w64-mingw32-g++` or `docker`, for cross-compiling executables for 64-bit Windows. The docker service must be up and running for this to work.
* `wine`, for testing executables compiled for 64-bit Windows (`cxx run`).
* `valgrind`, for profiling (`cxx valgrind`).
* `kcachegrind`, for viewing the information produced by *valgrind*.
* `gprof2dot` and `dot`, for producing a graph from the information produced by valgrind.
* `vagrant`, for testing *cxx* on other operating systems.
* `figlet`, for nicer output when running the `tests/build_all.sh` script, for building all the examples.
* Development packages for `SDL2`, `OpenGL`, `glut`, `glfw`, `sfml`, `GTK+3` and `Qt5`, for building and running the examples.
* `x86_64-w64-mingw32-g++` or `docker` is needed for building the `win64crate` example.
* `clang-format` for `cxx fmt`.

## C++23 on macOS

For installing a recent enough version of C++ on macOS, installing gcc 11 with `brew` is one possible approach:

    brew install gcc@11

The other requirements can be installed with:

    brew install scons make pkg-config

## C++23 on Arch Linux

g++ with support for `-std=c++2b` should already be installed.

Install scons and base-devel, if needed:

    pacman -S scons base-devel --needed

## C++23 on Debian or Ubuntu

You might need to install GCC 11 from the testing repository, or from a PPA.

Install build-essential, scons and pkg-config:

    apt install build-essential scons pkg-config

## C++23 on FreeBSD

FreeBSD 11.1 comes with C++17 support, but you may wish to install GCC 11 or later.

gcc11 or later should provide support for C++23.

Install pkg-conf, scons and gmake:

    pkg install pkgconf scons gmake

## Installation

Manual installation with `make` and `sudo`:

`sudo make install`

On FreeBSD, use `gmake` instead of `make`.

If possible, install *CXX* with the package manager that comes with your OS/distro.

## Uninstallation

`sudo make uninstall`

## One way of structuring projects

#### Filenames

* All include filenames should contain no spaces or special characters (a-z, A-Z, 0-9) and end with `.h` or `.hpp`.
* All C++ source filenames should contain no spaces or special characters (a-z, A-Z, 0-9) and end with `.cpp`, `.cc` or `.cxx`.
* The main source file could be named `main.cpp` or `main.cc`, but it does not have to.
* Files ending with `_test.*` are special, and will not be used when compiling the main executable(s).

#### Ninja

* Projects that already uses CMake (and need no extra command line arguments when running `cmake`) are also CXX compatible and can be built with CMake + Ninja like this:

    cxx ninja

#### QtCreator

The generated qmake/QtCreator project files were tested with QtCreator 4.6 on Arch Linux.

## Source code formatting

* `cxx fmt` will format C++23 source code in a single, fixed, formatting style (clang-format "Webkit"-style), which is not configurable, on purpose. Using `cxx fmt` is optional.

## Feedback

The goal is that every executable and project written in C++23 should be able to build with `cxx` on a modern Linux distro, FreeBSD or macOS system (with Homebrew), without any additional configuration.

If you have a project written in C++ that you think should be able to build with `cxx`, but doesn't, please create an issue and include a link to your repository.

## GNU Parallel

If running CXX with `parallel`, make sure to use the `--compress` or `--tmpdir` flag to change the location of the temporary SQLite database.

Example build target in a Makefile, for using `parallel` and `cxx`, while disabling warnings:

    build:
        +CXXFLAGS='$(CXXFLAGS) -w' parallel --compress cxx opt -C ::: subdir1 subdir2 subdir3

`subdir1`, `subdir2` and `subdir3` are just examples of directory names.

## OpenBSD

For OpenBSD, install g++ 11 and build with `cxx CXX=eg++`.

## GTK and Qt

* Only the latest version of GTK and Qt are supported. Currently, that's GTK+4 and Qt6. Please create an issue or submit a pull request if there are new releases of GTK or Qt.
* The GTK and Qt examples are currently only tested on Arch Linux.

## Editor Configuration

Syntastic settings for ViM and NeoVim:

    " If your compiler supports it, change "2b" to "23". If the compiler only supports C++17, use "17".
    let g:syntastic_cpp_compiler = 'g++'
    let g:syntastic_cpp_compiler_options = ' -std=c++2b -pipe -fPIC -fno-plt -fstack-protector-strong -Wall -Wshadow -Wpedantic -Wno-parentheses -Wfatal-errors -Wvla'
    let g:syntastic_cpp_include_dirs = ['../common', './common', '../include', './include']

    " Ignore some defines and warnings
    let g:syntastic_quiet_messages = {
        \ "!level": "errors",
        \ "regex":  [ 'RESOURCEDIR', 'RESDIR', 'DATADIR', 'IMGDIR', 'SHAREDIR', 'SHADERDIR', 'expected .*).* before string constant' ] }

## General info

* Version: 3.2.8
* License: BSD-3
* Author: Alexander F. Rødseth &lt;xyproto@archlinux.org&gt;
