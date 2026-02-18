#!/bin/bash
# build.sh
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating staticfiles directory..."
mkdir -p staticfiles

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Running migrations..."
python manage.py migrate

echo "Build complete!"