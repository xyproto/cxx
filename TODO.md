# TODO

- [ ] Void Linux support
- [ ] Document `sm script` and `sm make`
- [ ] Add `sm kdev` for exporting a KDevelop project file
- [ ] Add support for a `doc` directory that will be installed to the right place upon installation.

### Maybe

- [ ] The scons script and the SConstruct file can be combined to a single Python script, then compiled with nuitka
- [ ] Version number support. Semver in README.md? `#define VERSION` in the main sourcefile?
- [ ] `sm get` for downloading dependencies by looking up the missing filename online somewhere, then installing the package with the package manager.
- [ ] go-like includes like `#include <github.com/someproject/someproject.h#tag=sfdsdf>` and `#include <...#commit=asdf123>`, then `sm get` will git clone the deps in such a way that the include will be detected. Must exit with an error if the include, tag or commit does not exist.
- [ ] `sm vendor` to place git dependencies in a `vendor` directory as git submodules

### Some day

- [ ] Stop the linker error output after the first error. Send a patch upstream if this is not currently possible.
- [ ] Support spaces in directory names.
- [ ] Support spaces in source file names.
- [ ] Put platform support in well-defined classes
- [ ] Rewrite everything as one application, without depending on make or SCons
