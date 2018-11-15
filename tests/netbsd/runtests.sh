#!/bin/sh
set -v
sakemake/tests/all.py fastclean:build config gtk3 sfml smallpt vulkan vulkan_glfw qt5 win64crate entityx
