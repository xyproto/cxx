#!/bin/sh
scriptdir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$scriptdir"

docker build --no-cache -t cxx:void . && docker run --rm --name cxx_void cxx:void
