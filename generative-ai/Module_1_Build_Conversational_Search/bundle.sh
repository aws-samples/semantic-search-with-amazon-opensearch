#!/usr/bin/env bash

rm -rf dist

pip install --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: -r requirements.txt -t dist

# (optional when openai is used) openai doesn't have a binary distribution, so need a separate install
pip install -I openai -t dist 

# remove extraneous bits from installed packages
rm -r dist/*.dist-info
cp config.py chain_queryEncoder.py main_queryEncoder.py chain_documentEncoder.py main_documentEncoder.py dist/
cd dist && zip -r ../queryEncoder.zip *
zip -r ../documentEncoder.zip * -x queryEncoder.zip
rm -rf ../dist
cd ../webapp && zip -r ../webapp.zip *