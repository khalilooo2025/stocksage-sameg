#!/usr/bin/env bash
# Build script for Render.com deployment
set -o errexit

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Creating static directory if needed..."
mkdir -p static

echo "==> Collecting static files..."
python manage.py collectstatic --no-input --ignore="*.scss" --ignore="*.less"

echo "==> Running migrations..."
python manage.py migrate

echo "==> Loading seed data..."
python manage.py seed_data || echo "Seed data already loaded or skipped."

echo "==> Build complete!"
