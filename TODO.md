# TODO

### Priority 1

- [ ] Add a way to vendor a C++17 dependency via git from ie. GitHub.
- [ ] Add a `sm code` for exporting a VS Code project file.
- [ ] Add a simple way to write and provide man pages for projects.

### Priority 2

- [ ] NetBSD fastcgi example needs: -lfcgi -lfcgi++ -Wl,-R/usr/pkg/lib
- [ ] Add a `sm new` command for creating new projects.
- [ ] Rewrite everything so that SCons is not needed.
- [ ] Support spaces in directory names.
- [ ] Support spaces in source file names.

### Priority 3

- [ ] Use a "semver" compatible version number in `README.md`.
- [ ] Document `sm script` and `sm make`
- [ ] Add support for a `doc` directory that will be installed to the right place upon installation.

### Maybe

- [ ] Add "sm init" to init flags, checksum source code etc. Add "sm build" to build. Just "sm" should do both "init" and "build".
- [ ] `sm get` for downloading dependencies by looking up the missing filename online somewhere, then installing the package with the package manager.
- [ ] go-like includes like `#include <github.com/someproject/someproject.h#tag=sfdsdf>` and `#include <...#commit=asdf123>`, then `sm get` will git clone the deps in such a way that the include will be detected. Must exit with an error if the include, tag or commit does not exist.
- [ ] `sm vendor` to place git dependencies in a `vendor` directory as git submodules.
- [ ] Detect everything about the system into a .db file.
- [ ] Place every source file in a database before building?
- [ ] Stop the linker error output after the first error. Send a patch upstream if this is not currently possible.
- [ ] Put platform support in well-defined classes.
- [ ] Rewrite everything as one application, without depending on make or SCons.
