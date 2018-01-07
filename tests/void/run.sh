#!/bin/sh
docker build --no-cache -t sakemake:void . && docker run --rm sakemake:void
