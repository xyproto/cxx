#!/bin/sh
docker build --no-cache -t sakemake:void . && docker run --rm --name sakemake_void sakemake:void
