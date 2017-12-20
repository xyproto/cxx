# TODO

* Only add directories with `-I` on the command line that actually exists.
* When passing flags starting with `-W`, they should be passed directly to the compiler, like `-Wconversion` and `-Weffc++`
* The "extra" argument should also turn on `-Wconversion` and possibly also `-Weffc++`.
* Respect `$CXX` and `$CXXFLAGS`.
* When seeing includes like "stdio.h" and "stdint.h", don't look for them with `pkg-config`.
* Less noisy searches with `pkg-config`
* Support projects that include:
 * `#include "SDL/SDL.h"`.
 * `#include <stdio.h>`.
* If there is only one `.cpp` file in a directory, consider that one to be the "main.cpp" file.
