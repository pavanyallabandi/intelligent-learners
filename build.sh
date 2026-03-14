#!/bin/bash

# Build Script for Vercel
echo "Building project..."
python3 -m pip install -r requirements.txt

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Running migrations..."
python3 manage.py migrate
