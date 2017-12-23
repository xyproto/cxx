# :sake: sakemake

*Sakemake* is a build system that provides a simple way to build your C++17 executables, structure your C++17 code, test and debug your source files. It also makes it easy for Linux distro packagers to package your project, and for users to build and install it.

It uses scons, make and pkg-config under the hood, while providing a tool that aims to be as easy to use as `go build` for Go.

Dependencies, like SDL2 for example, are discovered automatically and the correct flags are given to the C++ compiler. The latest versions of both GCC (g++) and Clang (clang++) are supported.

**No configuration files needed!** No `CMakeLists.txt`, `Makefile`, `SConstruct`, `configure`, `automake`, `Makefile.in` or other acrobatics.

If you are building a library, *Sakemake* is not for you, yet. If you are looking for a configuration-free build system for C++17 on Linux, *Sakemake* might be for you.

Give it a spin and see if it behaves as expected?


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

    sm -C example/hello

#### Cleaning and building:

    sm rebuild

#### Installing on the local system, using sudo:

    sudo PREFIX=/usr sm install

The name of the current directory will be used as the executable name.

#### Packaging a project into $pkgdir:

    DESTDIR="$pkgdir" PREFIX=/usr sm install

--- or just ---

    sm pkg

The name of the current directory will be used as the executable name.

#### Strict compilation flags (complains about all things):

    sm strict

#### Sloppy compilation flags (will ignore all warnings):

    sm sloppy

#### Get the current version:

    sm version

## Features and limitations

* **No configuration needed**, as long as the *Sakemake* directory structure is followed.
* **Auto-detection** of include, define and libarary flags, based on which files are included from `/usr/include`, using **`pkg-config`**. Not all libraries, include files and cxxflags can be auto-detected yet, but more are to be added.
* Built-in support for testing, clang, debug builds and only rebuilding files that needs to be rebuilt.
* Uses the caching that is supplied by SCons, no ccache needed.
* Does not use a `build` directory, it's okay that the `main` executable ends up in the root folder of the project. `main.cpp` can be placed in the root folder of the project, or in its own directory.
* Only tested on Linux and macOS, but should work on any UNIX-like system.
* All source filenames must be lowercase.
* Your include files are expected to be placed in `./include` or `../include`.
* Source files used by multiple executables in your project are expected to be placed in `./common` or `../common`.
* Tests are expected to end with `_test.cpp` and will be ignored when building `main.cpp`.
* For now, *Sakemake* is only meant to be able to build executables, not libraries.
* See the `hello` example in the `example` directory for the suggested directory structure.

## Suggested directory structure

For a "Hello, World!" program that places the text-generation in a `std::string hello()` function, this is one way to structure the files:


```
.
├── hello/main.cpp
├── hello/include/hello.h
├── hello/include/test.h
├── hello/common/hello.cpp
└── hello/common/hello_test.cpp
```

#### --- or if you prefer a directory per executable ---

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

using std::cout;
using std::endl;

int main() {
  cout << hello() << endl;
  return 0;
}
```

**hello.h**

```c++
#pragma once

#include <string>

using std::string;
using namespace std::literals;

string hello();
```

**hello.cpp**

```c++
#include "hello.h"

string hello() {
  return "Hello, World!"s;
}
```

**hello_test.cpp**

```c++
#include "test.h"
#include "hello.h"

using namespace std::literals;

void hello_test() {
  equal(hello(), "Hello, World!"s);
}

int main() {
  hello_test();
  return 0;
}
```

**test.h**

```c++
#pragma once

#include <iostream>
#include <cstdlib>

using std::cout;
using std::endl;

template<typename T>
void equal(T a, T b) {
    if (a == b) {
        cout << "YES" << endl;
    } else {
        cout << "NO" << endl;
        exit(EXIT_FAILURE);
    }
}

```

## Requirements

* scons
* make
* pkg-config
* g++ with support for c++17
* clang++ with support for c++17

## C++17 on macOS

For installing a recent enough version of ++ on macOS, installing GCC with Homebrew and the `--HEAD` flag, is one possible approach:

    brew install gcc --HEAD

The other requirements can be installed with:

    brew install scons make pkg-config

## C++17 on Arch Linux

g++ with support for C++17 should already be installed. If not, try installing base-devel:

    pacman -S base-devel

The only other requirement, scons, can be installed with:

    pacman -S scons

## Installation

If possible, install *Sakemake* with the package manager that comes with your distro.

Manual installation with `make` and `sudo`:

`sudo make install`

## Uninstallation

`sudo make uninstall`

## Feedback

The ideal is that every executable and small-ish project written in C++17 should be able to build with `sakemake` on a modern Linux distro, without any additional configuration. If you have a project that _almost_ builds with `sakemake`, please create an issue and include a link to your repository.

## A badge for your project

If your project can be built with `sakemake`, you are hereby awarded this badge that you may include in the `README.md` file:

### Large badge

    [![sakemake award](https://raw.githubusercontent.com/xyproto/sakemake/master/img/sakemake_award.png)](https://github.com/xyproto/sakemake))

[![sakemake award](https://raw.githubusercontent.com/xyproto/sakemake/master/img/sakemake_award.png)](https://github.com/xyproto/sakemake)

### Medium badge

    [![sakemake award](https://raw.githubusercontent.com/xyproto/sakemake/master/img/sakemake_award_128x128.png)](https://github.com/xyproto/sakemake))

[![sakemake award](https://raw.githubusercontent.com/xyproto/sakemake/master/img/sakemake_award_128x128.png)](https://github.com/xyproto/sakemake)

### Small badge

    [![sakemake award](https://raw.githubusercontent.com/xyproto/sakemake/master/img/sakemake_award_72x72.png)](https://github.com/xyproto/sakemake))

[![sakemake award](https://raw.githubusercontent.com/xyproto/sakemake/master/img/sakemake_award_72x72.png)](https://github.com/xyproto/sakemake)

### Tiny badge

    [:sake:](https://github.com/xyproto/sakemake)

[:sake:](https://github.com/xyproto/sakemake)

## General info

* Version: 1.3
* Author: Alexander F Rødseth &lt;xyproto@archlinux.org&gt;
* License: MIT
