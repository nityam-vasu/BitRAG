#!/bin/bash
# BitRAG Web GUI - Run Script
# Starts the Flask web server for BitRAG

set -e

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  BitRAG Web GUI${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Check if Flask is installed
if ! pip show flask > /dev/null 2>&1; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

echo -e "${GREEN}Starting BitRAG Web GUI...${NC}"
echo -e "${GREEN}Open http://localhost:5000 in your browser${NC}"
echo ""

# Run the web app
cd "$SCRIPT_DIR"
python web_app.py
