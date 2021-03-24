#!/bin/bash

source activate biotite-gallery

cd /tmp/biotite-gallery/biotite-$1
sphinx-build ./doc ./build/doc
cd ./build
zip -r doc.zip doc
cd ..
mkdir dist
mv ./build/doc.zip ./dist/doc.zip
