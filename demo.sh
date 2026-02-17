#!/bin/bash
# BitRAG Quick Demo Script
# Shows basic usage without starting interactive mode

# Set path to source
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   ██╗   ██╗ ██████╗ ██╗██████╗                              ║"
echo "║   ██║   ██║██╔═══██╗██║██╔══██╗                             ║"
echo "║   ██║   ██║██║   ██║██║██║  ██║                             ║"
echo "║   ╚██╗ ██╔╝██║   ██║██║██║  ██║                             ║"
echo "║    ╚████╔╝ ╚██████╔╝██║██████╔╝                             ║"
echo "║     ╚═══╝   ╚═════╝ ╚═╝╚═════╝                              ║"
echo "║        1-bit LLM RAG System Demo                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Activate .venv if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
fi

echo ""
echo "=========================================="
echo "  Available Commands"
echo "=========================================="
echo ""
echo "Quick Start:"
echo "  ./run.sh                                    # Interactive mode"
echo "  ./run.sh --help                             # Show help"
echo ""
echo "Document Commands:"
echo "  ./run.sh upload data/test_document.pdf      # Upload PDF"
echo "  ./run.sh documents                          # List documents"
echo "  ./run.sh query \"What is this?\"             # Query"
echo "  ./run.sh chat                               # Chat mode"
echo ""
echo "System:"
echo "  ./run.sh status                             # Status"
echo "  ./run.sh model list                         # List models"
echo ""
echo "=========================================="
echo ""
echo -e "${CYAN}Try running: ./run.sh status${NC}"
