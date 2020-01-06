#!/usr/bin/env bash

# Change to the script directory
cd "$(dirname "$0")"
pip install -r app_requirements.txt -t package/
cp -R package sub/
cp -R package hub/
