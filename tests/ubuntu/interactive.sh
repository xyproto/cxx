#!/bin/sh
docker build --no-cache -t sakemake:ubuntu_18_10 .
docker run -it --name sakemake_ubuntu sakemake:ubuntu_18_10 bash
