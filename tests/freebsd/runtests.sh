#!/bin/sh
# config : found no suitable package
# fastcgi : found no suitable package
# sfml : problems with sf::String::String
# boost : compilation problems
# win64crate : not available?
# notify : compilation problems
# entityx : not available?
# qt5 : ?
# pytorch : not available?
#
cxx/tests/all.py fastclean:build config fastcgi sfml sfml_audio boost boost_thread win64crate notify entityx qt5 pytorch
