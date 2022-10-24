#!/bin/bash
cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" 
deactivate
source ubuntu_env/bin/activate
python3 app.py $@


