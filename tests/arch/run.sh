#!/bin/sh
scriptdir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$scriptdir"

#docker build -t cxx:arch . && docker run --rm --name cxx_arch cxx:arch
docker build --no-cache -t cxx:arch . && docker run --rm --name cxx_arch cxx:arch
