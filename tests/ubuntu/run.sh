#!/bin/sh
scriptdir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$scriptdir"

docker build --no-cache -t sakemake:ubuntu_17_10 . && docker run --rm --name sakemake_ubuntu sakemake:ubuntu_17_10
