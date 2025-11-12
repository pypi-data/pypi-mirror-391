#!/bin/bash

# Release Preparation Script
# This script prepares a release with the latest dependency versions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to get current version from pyproject.toml
get_current_version() {
    grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'
}

# Function to update version in pyproject.toml
update_version() {
    local new_version=$1
    sed -i.bak "s/^version = .*/version = \"$new_version\"/" pyproject.toml
    rm pyproject.toml.bak
}

echo -e "${BLUE}Release Preparation Script${NC}"
echo "========================="

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Get current version
CURRENT_VERSION=$(get_current_version)
echo -e "${YELLOW}Current version: $CURRENT_VERSION${NC}"

# Ask for new version if not provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Enter new version (or press Enter to keep current):${NC}"
    read -r NEW_VERSION
    if [ -z "$NEW_VERSION" ]; then
        NEW_VERSION=$CURRENT_VERSION
    fi
else
    NEW_VERSION=$1
fi

echo -e "${YELLOW}Preparing release version: $NEW_VERSION${NC}"

# Update version if changed
if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
    echo -e "${YELLOW}Updating version in pyproject.toml...${NC}"
    update_version "$NEW_VERSION"
fi

# Run the complete release workflow
echo -e "${YELLOW}Running complete release workflow...${NC}"
if make release-all; then
    echo -e "${GREEN}Release preparation completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Review the built package in the 'dist/' directory"
    echo "2. Test the package: pip install dist/mcp_tavily-$NEW_VERSION-py3-none-any.whl"
    echo "3. If everything looks good, upload with: make upload-latest"
    echo "4. Commit and tag the release:"
    echo "   git add ."
    echo "   git commit -m \"Release v$NEW_VERSION\""
    echo "   git tag v$NEW_VERSION"
    echo "   git push origin main --tags"
    echo ""
    echo -e "${GREEN}Dependencies used for this release:${NC}"
    source .venv/bin/activate
    pip list | grep -E "(mcp|pydantic|python-dotenv|tavily|pytest)" | head -20
else
    echo -e "${RED}Release preparation failed!${NC}"
    echo "Please review the errors above and fix any issues."
    exit 1
fi