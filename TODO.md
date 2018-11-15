# TODO

### Top priority

- [ ] NetBSD fastcgi example needs: -lfcgi -lfcgi++ -Wl,-R/usr/pkg/lib

### Yes

- [ ] Version number support. Semver in README.md? `#define VERSION` in the main sourcefile?
- [ ] Add "sm new" for creating new projects.
- [ ] Add `sm code` for exporting a VS Code project file
- [ ] Add a way to write and install man pages.

### Maybe

- [ ] Rewrite everything so that SCons is not needed.
- [ ] Add "sm init" to init flags, checksum source code etc. Add "sm build" to build. Just "sm" should do both "init" and "build".
- [ ] Document `sm script` and `sm make`
- [ ] Add support for a `doc` directory that will be installed to the right place upon installation.
- [ ] `sm get` for downloading dependencies by looking up the missing filename online somewhere, then installing the package with the package manager.
- [ ] go-like includes like `#include <github.com/someproject/someproject.h#tag=sfdsdf>` and `#include <...#commit=asdf123>`, then `sm get` will git clone the deps in such a way that the include will be detected. Must exit with an error if the include, tag or commit does not exist.
- [ ] `sm vendor` to place git dependencies in a `vendor` directory as git submodules
- [ ] Detect everything about the system into a .db file.
- [ ] Place every source file in a database before building?

### Some day

- [ ] Stop the linker error output after the first error. Send a patch upstream if this is not currently possible.
- [ ] Support spaces in directory names.
- [ ] Support spaces in source file names.
- [ ] Put platform support in well-defined classes
- [ ] Rewrite everything as one application, without depending on make or SCons

### Probably not

- [ ] The scons script and the SConstruct file can be combined to a single Python script, then compiled with nuitka
