#!/bin/bash

# Dependency Compatibility Test Script
# This script tests the project with the latest dependency versions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 Dependency Compatibility Test${NC}"
echo "================================="

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv .venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Backup current requirements
echo -e "${YELLOW}Backing up current dependencies...${NC}"
pip freeze > requirements-backup.txt

# Install latest versions
echo -e "${YELLOW}Installing latest dependency versions...${NC}"
if command -v uv &> /dev/null; then
    uv pip install -r requirements-dev.txt -U
    uv pip install -e .
else
    pip install -r requirements-dev.txt -U
    pip install -e .
fi

# Show what was installed
echo -e "${YELLOW}Installed dependency versions:${NC}"
pip list | grep -E "(mcp|pydantic|python-dotenv|tavily|pytest)"

# Run tests
echo -e "${YELLOW}Running compatibility tests...${NC}"
if python -W ignore -m pytest tests --cov=src/mcp_server_tavily --cov-report=term --verbose; then
    echo -e "${GREEN}✅ All tests passed with latest dependencies!${NC}"
    RESULT=0
else
    echo -e "${RED}❌ Tests failed with latest dependencies!${NC}"
    RESULT=1
fi

# Show dependency differences
echo -e "${YELLOW}Dependency changes:${NC}"
pip freeze > requirements-new.txt
if command -v diff &> /dev/null; then
    diff requirements-backup.txt requirements-new.txt || true
fi

# Cleanup
rm -f requirements-backup.txt requirements-new.txt

if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}🎉 Compatibility test completed successfully!${NC}"
    echo "Your project is compatible with the latest dependency versions."
else
    echo -e "${RED}💥 Compatibility test failed!${NC}"
    echo "Please review the test output and update your code accordingly."
    echo "You may need to:"
    echo "  1. Fix breaking changes in your code"
    echo "  2. Update your tests"
    echo "  3. Pin specific dependency versions in requirements.txt"
fi

exit $RESULT