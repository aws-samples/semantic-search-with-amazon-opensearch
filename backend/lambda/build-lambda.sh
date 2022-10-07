#!/bin/bash

pip install --target ./package -r requirements.txt

cd package
zip -r ../lambda.zip .

cd ..
zip -g lambda.zip app.py

