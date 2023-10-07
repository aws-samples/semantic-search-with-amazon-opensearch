#!/usr/bin/env bash

rm -rf dist

pip install --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: -r requirements.txt -t dist

# (optional when openai is used) openai doesn't have a binary distribution, so need a separate install
pip install -I openai -t dist 

# remove extraneous bits from installed packages
rm -r dist/*.dist-info
cp config.py chain.py main.py chain_s3.py main_s3.py dist/
cd dist && zip -r lambda.zip *
zip -r lambda_s3.zip * -x lambda.zip