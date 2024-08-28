#!/bin/bash

script_args=$@

echo "Run RCD Generator"
python3 gen/main_app.py -n ${script_args}
