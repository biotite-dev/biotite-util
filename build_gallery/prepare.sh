#!/bin/bash

rm -r /tmp/biotite-gallery
mkdir /tmp/biotite-gallery
cd /tmp/biotite-gallery

wget https://github.com/biotite-dev/biotite/archive/refs/tags/v$1.tar.gz
tar -xf v$1.tar.gz
cd biotite-$1

mamba remove -n biotite-gallery --all
mamba env create -n biotite-gallery -f environment.yml

source activate biotite-gallery
python setup.py install
