#!/bin/sh
# config : found no suitable package
# fastcgi : found no suitable package
# sfml : problems with sf::String::String
# boost : compilation problems
# win64crate : not available?
# notify : compilation problems
# entityx : not available?
# qt5 : ?
#
cxx/tests/all.py fastclean:build boost boost_thread config dunnetgtk entityx fastcgi mixer notify openal qt5 raylib sdl2 sdl2_opengl sfml sfml_audio smallpt synth vulkan vulkan_glfw win64crate x11 x11_opengl 
