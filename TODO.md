# TODO

### Priority 1

- [ ] Detect libraries without .so files, like RapidJSON, correctly.
- [ ] Add a way to compile static executables.
- [ ] If the `.pc` file for ie. glm returns no flags, don't consider it an error.
- [ ] Add `cxx optrec` and `cxx smallrec`, or find a better way.
- [ ] Add a way to vendor a c++2b dependency via git from ie. GitHub.
- [ ] Add a `cxx code` for exporting a VS Code project file.
- [ ] Add a simple way to write and provide man pages for projects.

### Priority 2

- [ ] NetBSD fastcgi example needs: -lfcgi -lfcgi++ -Wl,-R/usr/pkg/lib
- [ ] Add a `cxx new` command for creating new projects.
- [ ] Rewrite everything so that SCons is not needed.
- [ ] Support spaces in directory names.
- [ ] Support spaces in source file names.

### Priority 3

- [ ] Use a "semver" compatible version number in `README.md`.
- [ ] Document `cxx script` and `cxx make`
- [ ] Add support for a `doc` directory that will be installed to the right place upon installation.

### Maybe

- [ ] Add "cxx init" to init flags, checksum source code etc. Add "cxx build" to build. Just "sm" should do both "init" and "build".
- [ ] `cxx get` for downloading dependencies by looking up the missing filename online somewhere, then installing the package with the package manager.
- [ ] go-like includes like `#include <github.com/someproject/someproject.h#tag=sfdsdf>` and `#include <...#commit=asdf123>`, then `cxx get` will git clone the deps in such a way that the include will be detected. Must exit with an error if the include, tag or commit does not exist.
- [ ] `cxx vendor` to place git dependencies in a `vendor` directory as git submodules.
- [ ] Detect everything about the system into a .db file.
- [ ] Place every source file in a database before building?
- [ ] Stop the linker error output after the first error. Send a patch upstream if this is not currently possible.
- [ ] Put platform support in well-defined classes.
- [ ] Rewrite everything as one application, without depending on make or SCons.
- [ ] Parse all source files concurrently and place tokens in a SQLite database with "cxx slurp".
