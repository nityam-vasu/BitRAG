#!/bin/bash
# BitRAG Web GUI - Run Script
# Starts the Flask web server for BitRAG
#
# Usage:
#   ./run_web.sh                 Start web server (default: localhost:5000)
#   ./run_web.sh --port 8080     Start on specific port
#   ./run_web.sh --host 0.0.0.0  Bind to specific host
#   ./run_web.sh --help          Show this help message

set -e

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
PORT=5000
HOST="0.0.0.0"
NO_INSTALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "BitRAG Web GUI"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --help, -h              Show this help message"
            echo "  --port, -p <port>       Port to run server on (default: 5000)"
            echo "  --host, -H <host>       Host to bind to (default: 0.0.0.0)"
            echo "  --no-install            Skip dependency installation"
            echo "  --check                 Check system requirements only"
            echo ""
            echo "Examples:"
            echo "  $0                      # Start on localhost:5000"
            echo "  $0 --port 8080          # Start on port 8080"
            echo "  $0 --host 127.0.0.1     # Bind to localhost only"
            exit 0
            ;;
        --port|-p)
            PORT="$2"
            shift 2
            ;;
        --host|-H)
            HOST="$2"
            shift 2
            ;;
        --no-install)
            NO_INSTALL=true
            shift
            ;;
        --check)
            echo "Checking system requirements..."
            echo ""
            
            # Check Python
            if command -v python3 &> /dev/null; then
                python_version=$(python3 --version 2>&1)
                echo -e "${GREEN}✓ Python:${NC} $python_version"
            else
                echo -e "${RED}✗ Python 3 not found${NC}"
            fi
            
            # Check venv
            if [ -d "$SCRIPT_DIR/venv" ]; then
                echo -e "${GREEN}✓ Virtual environment found${NC}"
            else
                echo -e "${YELLOW}⚠ No virtual environment (will create one)${NC}"
            fi
            
            # Check Ollama
            if command -v ollama &> /dev/null; then
                ollama_version=$(ollama --version 2>&1)
                echo -e "${GREEN}✓ Ollama:${NC} $ollama_version"
            else
                echo -e "${YELLOW}⚠ Ollama not installed${NC}"
            fi
            
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        BitRAG Web GUI                          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Check if Flask is installed
if ! pip show flask > /dev/null 2>&1; then
    if [ "$NO_INSTALL" = true ]; then
        echo -e "${RED}✗ Flask not installed. Install dependencies first.${NC}"
        exit 1
    fi
    echo -e "${YELLOW}⚠ Installing dependencies...${NC}"
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

echo -e "${GREEN}✓ Starting BitRAG Web GUI...${NC}"
echo -e "${GREEN}✓ URL: http://${HOST}:${PORT}${NC}"
echo ""

# Run the web app
cd "$SCRIPT_DIR"
python web_app.py --port "$PORT" --host "$HOST"
