#!/bin/sh
set -v
python3.8 cxx/tests/all.py fastclean:build config gtk3 sfml smallpt vulkan vulkan_glfw qt5 win64crate entityx fastcgi
