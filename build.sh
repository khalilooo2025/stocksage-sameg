#!/usr/bin/env bash
# Build script for Render.com deployment
set -o errexit

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running migrations..."
python manage.py migrate

echo "==> Loading seed data..."
python manage.py seed_data || echo "Seed data already loaded or skipped."

echo "==> Build complete!"
