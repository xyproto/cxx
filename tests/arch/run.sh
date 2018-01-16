#!/bin/sh
docker build --no-cache -t sakemake:arch . && docker run --rm --name sakemake_arch sakemake:arch
