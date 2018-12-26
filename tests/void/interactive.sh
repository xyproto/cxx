#!/bin/sh
docker build --no-cache -t cxx:void .
docker run --rm -it --name cxx_void_interactive cxx:void bash
