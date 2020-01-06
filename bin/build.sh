#!/usr/bin/env bash

git clone https://github.com/tfutils/tfenv.git ~/.tfenv
echo 'export PATH="$HOME/.tfenv/bin:$PATH"' >> ~/.bash_profile

source ~/.bash_profile

cd /opt/subhub
pip3 install -r automation_requirements.txt
python3 dodo.py
