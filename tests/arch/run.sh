#!/bin/sh
scriptdir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$scriptdir"

#docker build -t sakemake:arch . && docker run --rm --name sakemake_arch sakemake:arch
docker build --no-cache -t sakemake:arch . && docker run --rm --name sakemake_arch sakemake:arch
