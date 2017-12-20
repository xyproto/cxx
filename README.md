# :sake: sake make

`sakemake` is a small program that provides a simple way to build your C++17 executables, structure your C++17 code, test and debug your source files.

It uses SCons, make and pkg-config under the hood, while providing a tool that aims to be as easy to use as `go build` for Go.

Dependencies, like for example SDL2, are discovered automatically and the correct flags are given to the C++ compiler. The latest versions of both GCC (g++) and Clang (clang++) are supported.

No configuration files are needed! No `CMakeLists.txt`, `Makefile`, `SConstruct`, `configure`, `automake`, `Makefile.in` or other acrobatics.

If you are building a library, `sakemake` is not for you yet. If you are looking for a configuration-free build system for C++17 on Linux, `sakemake` might be for you. You can give it a go and see if it works for what you are trying to achieve.


## Usage

In a directory with C++17 source files ending with `.cpp`, and a `main.cpp` file, building is as simple as:

    sakemake

Build and run:

    sakemake run

Build and run tests in a directory with files ending with `_test.cpp`:

    sakemake test

Clean:

    sakemake clean

Build with clang instead of gcc:

    sakemake clang

Debug build:

    sakemake debug

Building a specific directory (`sakemake` takes the same options as `make`):

    sakemake -C example/hello


## Features and limitations

* Auto-detect of include, define and libarary flags, based on which files are included from `/usr/include`, using `pkg-config`.
* **No configuration needed**, as long as the *sakemake* directory structure is followed.
* Built-in support for testing, clang, debug builds and only rebuilding files that needs to be rebuilt.
* Uses the caching that is supplied by SCons, no ccache needed.
* Does not use a `build` directory, it's okay that the `main` executable ends up in the same directory as `main.cpp`. Additional source files can be placed in other directories to avoid clutter.
* All filenames must be in lowercase.
* Only tested on Linux, but should work on any UNIX-like system that has the required dependencies.
* Include files are expected to be found in `../include`.
* Common `.cpp` files (the corresponding code to header files in ../include) are expected to be found in `../common`.
* Tests are expected to end with `_test.cpp` and will be ignored when building `main.cpp`.
* For now, `sakemake` is meant to be able to build executables, but not libraries.


## Suggested directory structure

For a "Hello, World!" program that places the text-generation in a `std::string hello()` function:


```
hello/main.cpp
hello/include/hello.h
hello/include/test.h
hello/common/hello.cpp
hello/common/hello_test.cpp
```

#### --- or if you prefer a `src` directory ---

```
hello/src/main.cpp
hello/include/hello.h
hello/include/test.h
hello/common/hello.cpp
hello/common/hello_test.cpp
```

**main.cpp**

```
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

```
#pragma once

#include <string>

using std::string;
using namespace std::literals;

string hello();
```

**hello.cpp**

```
#include "hello.h"

string hello() {
  return "Hello, World!"s;
}
```

**hello_test.cpp**

```
#include "test.h"
#include "hello.h"

void hello_test() {
  equal(hello(), "Hello, World!"s);
}

int main() {
  hello_test();
  return 0;
}
```

**test.h**

```
#pragma once

#include <iostream>
#include <cstdlib>

using std::cout;
using std::endl;
using namespace std::literals;

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

With your distro package manager, or with sudo:

`sudo make install`

In a package:

`make PREFIX="$pkgdir" install`

# Optional symlink

`sudo ln -s /usr/bin/sakemake /usr/bin/sm`

## Uninstallation

`sudo make uninstall`

## Awards for you project

If your project can be built with `sakemake`, and if you want to, you are allowed to include this badge in your `README.md` file, using this Markdown code:

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



## Version

0.2

## License

MIT
