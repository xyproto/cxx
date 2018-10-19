#!/bin/sh
scriptdir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$scriptdir"

docker build --no-cache -t sakemake:void . && docker run --rm --name sakemake_void sakemake:void
