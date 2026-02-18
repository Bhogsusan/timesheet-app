#!/bin/bash
# build.sh
set -o errexit

# Force Python 3.11
export PYTHON_VERSION=3.11.0

echo "Python version:"
python --version

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating staticfiles directory..."
mkdir -p staticfiles

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Running migrations..."
python manage.py migrate

echo "Build complete!"