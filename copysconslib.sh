#!/bin/sh

# This did not work. See github.com/SCons/scons

(cd scons; python boostrap.py build/scons)
(cd scons/src; python2 setup.py install --standalone-lib)
cp -rv scons/src/SCons sconslib
