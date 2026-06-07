#!/usr/bin/env bash
# Render ejecuta este script en cada deploy.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate