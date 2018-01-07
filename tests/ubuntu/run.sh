#!/bin/sh
docker build --no-cache -t sakemake:ubuntu_17_10 . && docker run --rm sakemake:ubuntu_17_10
