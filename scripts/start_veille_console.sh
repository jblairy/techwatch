#!/bin/bash
# Script de lancement du service console de veille (nouveau service séparé)
cd "$(dirname "$0")/.."
source .venv/bin/activate
python3 veille_service.py "$@"
