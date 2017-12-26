# TODO

* [ ] Strip unused dynamic library links (ldd / otool -L), perhaps by analyzing symbols before adding `-l` when compiling.
* [ ] Add support for using a `.cpp` file that is not "main.cpp" as the main source file, if it's the only one in a directory.
* [ ] Add a method for having an executable access a resource both when developing and after installing to a system.
