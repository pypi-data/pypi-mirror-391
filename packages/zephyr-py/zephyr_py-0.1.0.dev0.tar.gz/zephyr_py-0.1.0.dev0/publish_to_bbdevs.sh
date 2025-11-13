#!/bin/bash

# Script to build and publish Zephyr framework to bbdevs PyPI registry

set -e

echo "🔨 Building Zephyr framework..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

echo "📦 Built packages:"
ls -la dist/

echo "🚀 Publishing to bbdevs registry..."

# Upload to bbdevs registry
# Make sure ~/.pypirc is configured with bbdevs credentials
twine upload --repository bbdevs dist/*

echo "✅ Successfully published to https://pypi.bbdevs.com/bbdevs/"
echo "📥 Install with: pip install --index-url https://pypi.bbdevs.com/bbdevs/simple/ zephyr"
