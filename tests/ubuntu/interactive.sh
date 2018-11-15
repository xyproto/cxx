#!/bin/sh
docker build --no-cache -t sakemake:ubuntu_18_10 .
docker run --rm -it --name sakemake_ubuntu_interactive sakemake:ubuntu_18_10 bash
