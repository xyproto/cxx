#!/bin/sh
docker build -t sakemake_ubuntu_17_10 .
docker run -t sakemake_ubuntu_17_10
