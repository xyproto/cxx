# :sake: sake make

Opinionated build system that uses Python (Python2 in Scons) together with Make for compiling C++17 code.

No configuration needed.


## Usage

In a directory with C++17 source files ending with `.cpp`, and a `main.cpp` file, just:

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

* **No configuration needed**, as long as the *sakemake* directory structure is followed.
* Built-in support for testing, clang, debug builds and only rebuilding files that needs to be rebuilt.
* Uses the caching that is supplied by SCons, no ccache needed.
* Does not use a `build` directory, it's okay that the `main` executable ends up in the same directory as `main.cpp`. Additional source files can be placed in other directories to avoid clutter.
* All filenames must be in lowercase.
* Only tested on Linux, but should work on any UNIX-like system that has the required dependencies.
* Include files are expected to be found in `../include`.
* Common `.cpp` files (the corresponding code to header files in ../include) are expected to be found in `../common`.
* Tests are expected to end with `_test.cpp` and will be ignored when building `main.cpp`.


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

* Scons
* Make

## Installation

With your distro package manager, or with sudo:

`sudo make install`

In a package:

`make PREFIX="$pkgdir" install`

# Optional symlink

`sudo ln -s /usr/bin/sakemake /usr/bin/sm`

## Uninstallation

`sudo make uninstall`

## Version

0.1

## License

MIT
