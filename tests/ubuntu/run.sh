#!/bin/sh
docker build --no-cache -t sakemake_ubuntu_17_10 . && docker run --rm -t sakemake_ubuntu_17_10
