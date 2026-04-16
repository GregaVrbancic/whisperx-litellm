#!/usr/bin/env bash
# Script to update WhisperX version across the project

set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/update-whisperx-version.sh <version>"
    echo "Example: ./scripts/update-whisperx-version.sh 3.1.1"
    exit 1
fi

VERSION="$1"

echo "Updating WhisperX version to $VERSION..."

# Update .whisperx-version file
echo "WHISPERX_VERSION=$VERSION" > .whisperx-version

# Update pyproject.toml
sed -i '' "s/^version = \"[^\"]*\"/version = \"$VERSION\"/" pyproject.toml

echo "✓ Updated .whisperx-version"
echo "✓ Updated pyproject.toml"
echo ""
echo "WhisperX version updated to $VERSION"
echo "Don't forget to commit and tag this update!"
