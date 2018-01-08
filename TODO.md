# TODO

- [ ] Void Linux support
- [ ] `sm get` for downloading dependencies by looking up the missing filename online somewhere, then installing the package with the package manager.
- [ ] Add support for a `doc` directory that will be installed to the right place upon installation.
- [ ] The scons script and the SConsctruct file can be combined to a single Python script, then compiled with nuitka
- [ ] The things happening in the Makefile can be moved to a Python script
- [ ] If everything is in Python, it can be converted to Go with Grumpy

### Maybe

- [ ] Version number support. Semver in README.md? `#define VERSION` in the main sourcefile?
- [ ] go-like includes like `#include <github.com/someproject/someproject.h#tag=sfdsdf>` and `#include <...#commit=asdf123>`, then `sm get` will git clone the deps in such a way that the include will be detected. Must exit with an error if the include, tag or commit does not exist.
- [ ] `sm vendor` to place git dependencies in a `vendor` directory as git submodules

### Some day

- [ ] Stop the linker error output after the first error. Send a patch upstream if this is not currently possible.
- [ ] Support spaces in directory names.
- [ ] Support spaces in source file names.
