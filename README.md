# :sake: sakemake

`sakemake` is a small program that provides a simple way to build your C++17 executables, structure your C++17 code, test and debug your source files. It also makes it easy for Linux distro packagers to package your project, and for users to build and install it.

It uses SCons, make and pkg-config under the hood, while providing a tool that aims to be as easy to use as `go build` for Go.

Dependencies, like for example SDL2, are discovered automatically and the correct flags are given to the C++ compiler. The latest versions of both GCC (g++) and Clang (clang++) are supported.

No configuration files are needed! No `CMakeLists.txt`, `Makefile`, `SConstruct`, `configure`, `automake`, `Makefile.in` or other acrobatics.

If you are building a library, `sakemake` is not for you yet. If you are looking for a configuration-free build system for C++17 on Linux, `sakemake` might be for you. You can give it a go and see if it works for what you are trying to achieve.


## Usage

In a directory with C++17 source files ending with `.cpp`, and a `main.cpp` file, building is as simple as:

    sakemake

#### Build and run:

    sakemake run

#### Build and run tests in a directory with files ending with `_test.cpp`:

    sakemake test

#### Clean:

    sakemake clean

#### Build with clang instead of gcc:

    sakemake clang

#### Debug build:

    sakemake debug

#### Building a specific directory (`sakemake` can take the same flags as `make`):

    sakemake -C example/hello

#### Cleaning and building:

    sakemake rebuild

#### Installing on the local system, using sudo:

    sudo PREFIX=/usr sakemake install

The name of the current directory will be used as the executable name.

#### Packaging a project into $pkgdir:

    DESTDIR="$pkgdir" PREFIX=/usr sakemake install

The name of the current directory will be used as the executable name.

## Features and limitations

* **No configuration needed**, as long as the *sakemake* directory structure is followed.
* **Auto-detection** of include, define and libarary flags, based on which files are included from `/usr/include`, using **`pkg-config`**. Not all libraries, include files and cxxflags can be auto-detected yet, but more are to be added.
* Auto-detection of SDL2 is always supported.
* Built-in support for testing, clang, debug builds and only rebuilding files that needs to be rebuilt.
* Uses the caching that is supplied by SCons, no ccache needed.
* Does not use a `build` directory, it's okay that the `main` executable ends up in the root folder of the project. `main.cpp` can be placed in the root folder of the project, or in its own directory.
* Only tested on Linux and macOS, but should work on any UNIX-like system.
* All source filenames must be lowercase.
* Your include files are expected to be placed in `./include` or `../include`.
* Source files used by multiple executables in your project are expected to be placed in `./common` or `../common`.
* Tests are expected to end with `_test.cpp` and will be ignored when building `main.cpp`.
* For now, `sakemake` is meant to be able to build executables, not libraries.
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

#### --- or if you prefer a `src` directory ---

```
.
└── hello/src/main.cpp
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

* SCons
* Make
* pkg-config

## Installation

Prefer to install sakemake with your distro package manager, if possible.

System-wide, using sudo:

`sudo make install`

When creating a package:

`DESTDIR="$pkgdir" make install`

## Uninstallation

`sudo make uninstall`

## Feedback

The ideal is that every executable and small-ish project written in C++17 should be able to build with `sakemake` on a modern Linux distro, without any additional configuration. If you have a project that _almost_ builds with `sakemake`, please create an issue and include a link to your repository.

## Awards for you project

If your project can be built with `sakemake`, and if you want to, you can include this badge in your `README.md` file, using this Markdown code:

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

* License: MIT
* Version: 0.6
* Author: Alexander F Rødseth &lt;xyproto@archlinux.org&gt;

## Cat

:cat:
