#!/bin/bash
# BitRAG - Quick Install & Run
# Minimal version for demo showcase
#
# Usage:
#   ./install.sh                 Run full installation
#   ./install.sh --venv <dir>   Use custom venv directory
#   ./install.sh --skip-deps     Skip dependency installation
#   ./install.sh --help          Show this help message

set -e

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
VENV_DIR="venv"
SKIP_DEPS=false
CHECK_ONLY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "BitRAG Installer"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --help, -h              Show this help message"
            echo "  --venv, -v <dir>        Virtual environment directory (default: venv)"
            echo "  --skip-deps             Skip dependency installation"
            echo "  --check                 Check system requirements only"
            echo ""
            echo "Examples:"
            echo "  $0                      # Full installation"
            echo "  $0 --venv myenv         # Use myenv as venv directory"
            echo "  $0 --skip-deps          # Skip pip install (already installed)"
            exit 0
            ;;
        --venv|-v)
            VENV_DIR="$2"
            shift 2
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --check)
            CHECK_ONLY=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

show_banner() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              BitRAG Installer                  ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_system() {
    echo -e "${BLUE}Checking system...${NC}"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1)
        echo -e "${GREEN}✓ Python:${NC} $python_version"
    else
        echo -e "${RED}✗ Python 3 not found${NC}"
        return 1
    fi
    
    # Check pip
    if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
        echo -e "${GREEN}✓ pip found${NC}"
    else
        echo -e "${RED}✗ pip not found${NC}"
    fi
    
    # Check Ollama
    if command -v ollama &> /dev/null; then
        ollama_version=$(ollama --version 2>&1)
        echo -e "${GREEN}✓ Ollama:${NC} $ollama_version"
    else
        echo -e "${YELLOW}⚠ Ollama not found (optional)${NC}"
    fi
}

install() {
    echo -e "${BLUE}[1/4] Creating virtual environment...${NC}"
    
    if [ -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
    else
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}✓ Created at $VENV_DIR${NC}"
    fi

    # Activate
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    echo -e "${BLUE}[2/4] Upgrading pip...${NC}"
    pip install --upgrade pip #--quiet
    echo -e "${GREEN}✓ pip upgraded${NC}"

    # Install dependencies
    if [ "$SKIP_DEPS" = false ]; then
        echo -e "${BLUE}[3/4] Installing dependencies (this may take 5-10 minutes)...${NC}"
        pip install -e . #--quiet
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠ Skipping dependency installation${NC}"
    fi

    # Create directories
    echo -e "${BLUE}[4/4] Creating directories...${NC}"
    mkdir -p data chroma_db sessions
    echo -e "${GREEN}✓ Directories created${NC}"

    # Check Ollama
    echo ""
    echo -e "${BLUE}Checking Ollama...${NC}"
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}✓ Ollama is installed${NC}"
        if pgrep -x "ollama" > /dev/null; then
            echo -e "${GREEN}✓ Ollama is running${NC}"
        else
            echo -e "${YELLOW}⚠ Ollama not running. Start with: ${CYAN}ollama serve${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Ollama not found${NC}"
        echo "   Install from: https://ollama.ai"
    fi
}

show_next_steps() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              Installation Complete!             ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "  ${GREEN}1.${NC} Activate virtual environment:"
    echo "     source $VENV_DIR/bin/activate"
    echo ""
    echo "  ${GREEN}2.${NC} Download a model:"
    echo "     ./download_models.sh"
    echo ""
    echo "  ${GREEN}3.${NC} Run BitRAG:"
    echo "     ./run_web.sh        # Web UI at http://localhost:5000"
    echo "     ./run.sh            # Terminal UI"
    echo "     bitrag --help       # CLI help"
    echo ""
}

# Main execution
show_banner

# Check system
if ! check_system; then
    exit 1
fi

if [ "$CHECK_ONLY" = true ]; then
    exit 0
fi

# Install
install

# Show next steps
show_next_steps
