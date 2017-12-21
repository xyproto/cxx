# TODO

* When passing flags starting with `-W`, they should be passed directly to the compiler, like `-Wconversion` and `-Weffc++`
* Respect `$CXX` and `$CXXFLAGS`.
* When seeing includes like "stdio.h" and "stdint.h", don't look for them with `pkg-config`.
* Less noisy searches with `pkg-config`
* Support projects that include:
 * `#include "SDL/SDL.h"`.
 * `#include <stdio.h>`.
* If there is only one `.cpp` file in a directory, consider that one to be the "main.cpp" file.
* Implement `sakemake install` for installing on the system (/usr/bin for Linux, /usr/local/bin for macOS)
* Implement `sakemake package <directory>` for installing to a given directory (DESTDIR) with PREFIX set to /usr or /usr/local. Package should also install the LICENSE or COPYTING file, if available.
* Implement `sakemake export` for placing Makefile and SConstruct in the current directory.
