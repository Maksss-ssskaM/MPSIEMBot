#!/bin/bash

if [ ! -d "venv" ]; then
  python -m venv venv
fi

if [[ "$OSTYPE" == "win32" || "$OSTYPE" == "msys" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

if ! pip freeze | grep -f <(sed 's/==.*//' requirements.txt); then
  pip install -r requirements.txt
fi