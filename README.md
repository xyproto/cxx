# [:sake:](https://github.com/xyproto/sakemake) Sakemake [![Build Status](https://travis-ci.org/xyproto/sakemake.svg?branch=master)](https://travis-ci.org/xyproto/sakemake)

*Sakemake* is a build system that provides a simple way to build your C++17 executables, structure your C++17 code, test and debug your source files. It also makes it easy for Linux (or Homebrew) packagers to package your project, and for users to build and install it.

It uses scons, make and pkg-config under the hood, while providing a tool that aims to be as easy to use as `go build` for Go.

**No configuration files are needed!** No `CMakeLists.txt`, `Makefile`, `SConstruct`, `configure`, `automake` or `Makefile.in`.

Dependencies are discovered automatically, and the correct flags are given to the C++ compiler. If the dependencies are discovered correctly, the project is *Sakemake*-compliant and may display the badge below as a guarantee for users that the project will be easy to deal with.

The latest versions of both GCC (g++) and Clang (clang++) are supported.

If you are developing a C++ library, *Sakemake* is not for you, yet. However, if you are looking for a configuration-free build system executables written in C++17, on Linux, macOS or FreeBSD, *Sakemake* **might** be for you. The only way to be sure is to give it a spin.


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

#### Packaging a project into $pkgdir:

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

## Features and limitations

* **No configuration files are needed**, as long as the *Sakemake* directory structure is followed.
* **Auto-detection** of include, define and library flags, based on which files are included from `/usr/include`, using **`pkg-config`**. It also uses system-specific ways of attempting to detect which packages provides which compilation flags. Not all libraries, include files and cxxflags can be auto-detected yet, but more are to be added.
* Built-in support for testing, clang, debug builds and only rebuilding files that needs to be rebuilt.
* Uses the caching that is supplied by SCons, no ccache needed.
* Does not use a `build` directory, it's okay that the `main` executable ends up in the root folder of the project. `main.cpp` can be placed in the root folder of the project, or in its own directory.
* Only tested on Linux, FreeBSD and macOS. Should be easy to port to other systems that also has a package manager and pkg-config (or equivalent way to discover build flags).
* All source filenames must be lowercase.
* Your include files are expected to be placed in `./include` or `../include`.
* Source files used by multiple executables in your project are expected to be placed in `./common` or `../common`.
* Tests are expected to end with `_test.cpp` and will be ignored when building `main.cpp`.
* For now, *Sakemake* is only meant to be able to build executables, not libraries.
* See the `hello` example in the `examples` directory for the suggested directory structure.

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
* (clang++ with support for c++17)

## Path replacements at installation-time

Paths in `main.cpp`, `main.cc` or `main.cxx` are replaced at installation/packaging time (`sm install` or `sm pkg`):

* `"img/` is replaced with the full path to the `$PREFIX/share/name/img` directory, for instance `/usr/share/application_name/img`
* These strings are recognized and replaced: `"img/`, `"data/`, `"resources/`, `./img`, `./data` and `./resources`

This makes it easy to have an `img`, `data` or `resources` directory where files can be found and used both at development and at installation-time.

## C++17 on macOS

For installing a recent enough version of C++ on macOS, installing GCC with Homebrew and the `--HEAD` flag is one possible approach:

    brew install gcc --HEAD

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

## Feedback

The ideal is that every executable and project written in C++17 should be able to build with `sakemake` on a modern Linux distro, FreeBSD or macOS system (with homebrew), without any additional configuration.

If you have a project written in C++17 that you think should build with `sakemake`, but doesn't, please create an issue and include a link to your repository.

## A badge for your project

If your project can be built with `sakemake`, you are hereby awarded this badge that you may include in your `README.md` file:

### Large badge

[![configuration-free](https://raw.githubusercontent.com/xyproto/sakemake/master/img/configuration_free_256.png)](https://github.com/xyproto/sakemake)

    [![configuration-free](https://raw.githubusercontent.com/xyproto/sakemake/master/img/configuration_free_256.png)](https://github.com/xyproto/sakemake))

---

### Medium badge

[![configuration-free](https://raw.githubusercontent.com/xyproto/sakemake/master/img/configuration_free_128.png)](https://github.com/xyproto/sakemake)

    [![configuration-free](https://raw.githubusercontent.com/xyproto/sakemake/master/img/configuration_free_128.png)](https://github.com/xyproto/sakemake))

---

### Small badge

[![configuration-free](https://raw.githubusercontent.com/xyproto/sakemake/master/img/configuration_free_72.png)](https://github.com/xyproto/sakemake)

    [![configuration-free](https://raw.githubusercontent.com/xyproto/sakemake/master/img/configuration_free_72.png)](https://github.com/xyproto/sakemake))

---

### Tiny badge

[:sake:](https://github.com/xyproto/sakemake)

    [:sake:](https://github.com/xyproto/sakemake)

---

## General info

* Version: 1.31
* License: MIT
* Author: Alexander F Rødseth &lt;xyproto@archlinux.org&gt;
