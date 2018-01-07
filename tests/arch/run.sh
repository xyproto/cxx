#!/bin/sh
docker build --no-cache -t sakemake:arch . && docker run --rm sakemake:arch
