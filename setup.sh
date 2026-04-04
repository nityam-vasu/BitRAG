#!/bin/bash
# BitRAG Setup Script
# Sets up the BitRAG environment with virtual environment and dependencies
#
# Usage:
#   ./setup.sh                 Run full setup
#   ./setup.sh --venv <dir>   Use custom venv directory
#   ./setup.sh --skip-venv    Skip venv creation
#   ./setup.sh --skip-deps    Skip dependency installation
#   ./setup.sh --skip-ollama  Skip Ollama check
#   ./setup.sh --help         Show this help message

set -e

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default values
VENV_DIR=".venv"
SKIP_VENV=false
SKIP_DEPS=false
SKIP_OLLAMA=false
CHECK_ONLY=false
QUIET=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "BitRAG Setup"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --help, -h              Show this help message"
            echo "  --quiet, -q             Run in quiet mode (minimal output)"
            echo "  --venv, -v <dir>        Virtual environment directory (default: .venv)"
            echo "  --skip-venv             Skip virtual environment creation"
            echo "  --skip-deps             Skip dependency installation"
            echo "  --skip-ollama           Skip Ollama check"
            echo "  --check                 Check system requirements only"
            echo ""
            echo "Examples:"
            echo "  $0                      # Full setup"
            echo "  $0 -q                   # Full setup with minimal output"
            echo "  $0 --venv myenv        # Use myenv as venv directory"
            echo "  $0 --skip-ollama       # Skip Ollama check"
            exit 0
            ;;
        --quiet|-q)
            QUIET=true
            shift
            ;;
        --venv|-v)
            VENV_DIR="$2"
            shift 2
            ;;
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --skip-ollama)
            SKIP_OLLAMA=true
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
    if [ "$QUIET" = true ]; then
        return
    fi
    echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              BitRAG Setup                        ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
}

log() {
    if [ "$QUIET" = true ]; then
        return
    fi
    echo -e "$1"
}

check_python() {
    log "${BLUE}Checking Python...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        log "${RED}✗ Python 3 not found!${NC}"
        echo "  Please install Python 3.8 or higher."
        return 1
    fi
    
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    log "${GREEN}✓ Python version: $python_version${NC}"
    return 0
}

setup_venv() {
    log "${BLUE}Setting up virtual environment...${NC}"
    
    if [ -d "$VENV_DIR" ]; then
        log "${YELLOW}⚠ Virtual environment already exists at $VENV_DIR${NC}"
        read -p "Recreate it? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
        else
            log "${GREEN}✓ Using existing virtual environment${NC}"
            return 0
        fi
    fi
    
    log "${CYAN}Creating virtual environment at $VENV_DIR...${NC}"
    python3 -m venv "$VENV_DIR"
    log "${GREEN}✓ Virtual environment created${NC}"
}

activate_venv() {
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        log "${RED}✗ Virtual environment not found at $VENV_DIR${NC}"
        return 1
    fi
    
    source "$VENV_DIR/bin/activate"
    log "${GREEN}✓ Virtual environment activated${NC}"
}

install_deps() {
    log "${BLUE}Installing dependencies...${NC}"
    
    # Upgrade pip (show progress unless quiet mode)
    if [ "$QUIET" = true ]; then
        pip install --upgrade pip -q
    else
        pip install --upgrade pip
    fi
    log "${GREEN}✓ pip upgraded${NC}"
    
    # Install package in editable mode
    if [ "$QUIET" = true ]; then
        pip install -e . -q
    else
        pip install -e .
    fi
    log "${GREEN}✓ BitRAG installed${NC}"
}

create_dirs() {
    log "${BLUE}Creating directories...${NC}"
    mkdir -p data chroma_db sessions
    log "${GREEN}✓ Directories created${NC}"
}

check_ollama() {
    echo ""
    log "${BLUE}Checking Ollama...${NC}"
    
    if command -v ollama &> /dev/null; then
        ollama_version=$(ollama --version 2>&1)
        log "${GREEN}✓ Ollama installed: $ollama_version${NC}"
        
        if pgrep -x "ollama" > /dev/null; then
            log "${GREEN}✓ Ollama is running${NC}"
        else
            log "${YELLOW}⚠ Ollama not running${NC}"
            echo "  Start with: ${CYAN}ollama serve${NC}"
        fi
    else
        log "${YELLOW}⚠ Ollama not found${NC}"
        echo "  Install from: https://ollama.com"
    fi
}

show_next_steps() {
    echo ""
    log "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
    log "${CYAN}║              Setup Complete!                     ║${NC}"
    log "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "  ${GREEN}1.${NC} Activate virtual environment:"
    echo "     source $VENV_DIR/bin/activate"
    echo ""
    echo "  ${GREEN}2.${NC} Start Ollama (if not running):"
    echo "     ollama serve"
    echo ""
    echo "  ${GREEN}3.${NC} Download a model:"
    echo "     ./download_models.sh"
    echo ""
    echo "  ${GREEN}4.${NC} Run BitRAG:"
    echo "     ./run_web.sh        # Web UI"
    echo "     ./run.sh            # TUI"
    echo "     bitrag --help       # CLI help"
    echo ""
}

# Main execution
show_banner

# Check Python
if ! check_python; then
    exit 1
fi

# Check only mode
if [ "$CHECK_ONLY" = true ]; then
    echo ""
    exit 0
fi

# Setup virtual environment
if [ "$SKIP_VENV" = false ]; then
    setup_venv
fi

# Activate venv
activate_venv

# Install dependencies
if [ "$SKIP_DEPS" = false ]; then
    install_deps
fi

# Create directories
create_dirs

# Check Ollama
if [ "$SKIP_OLLAMA" = false ]; then
    check_ollama
fi

# Show next steps
show_next_steps
