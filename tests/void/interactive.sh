#!/bin/sh
docker build --no-cache -t sakemake:void .
docker run --rm -it --name sakemake_void_interactive sakemake:void bash
