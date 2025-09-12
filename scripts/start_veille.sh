#!/bin/bash
cd "$(dirname "$0")/.."
source .venv/bin/activate
python gui_main.py >> var/logs/gui_startup.log 2>&1
