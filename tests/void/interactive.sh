#!/bin/sh
docker build --no-cache -t sakemake:void .
docker run -it --name sakemake_void sakemake:void bash
