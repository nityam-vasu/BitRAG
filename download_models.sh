#!/bin/bash
# BitRAG Model Downloader
# Downloads Ollama models specified in OLLAMA_MODELS.txt
#
# Usage:
#   ./download_models.sh              Download all models from OLLAMA_MODELS.txt
#   ./download_models.sh --list       List models in OLLAMA_MODELS.txt
#   ./download_models.sh --model <m>  Download specific model
#   ./download_models.sh --help        Show this help message

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
COMMAND=""
MODEL_NAME=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "BitRAG Model Downloader"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --help, -h          Show this help message"
            echo "  --list, -l          List models in OLLAMA_MODELS.txt"
            echo "  --model, -m <name>  Download specific model"
            echo "  --check, -c         Check Ollama status only"
            echo ""
            echo "Examples:"
            echo "  $0                   # Download all models"
            echo "  $0 --list            # List available models"
            echo "  $0 --model llama3.2:1b  # Download specific model"
            exit 0
            ;;
        --list|-l)
            COMMAND="list"
            shift
            ;;
        --model|-m)
            COMMAND="download"
            MODEL_NAME="$2"
            shift 2
            ;;
        --check|-c)
            COMMAND="check"
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
    echo -e "${CYAN}║        BitRAG Model Downloader                 ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Check if Ollama is installed
check_ollama() {
    if ! command -v ollama &> /dev/null; then
        echo -e "${RED}✗ Ollama is not installed!${NC}"
        echo ""
        echo "Please install Ollama first:"
        echo "   curl -fsSL https://ollama.com/install.sh | sh"
        return 1
    fi
    echo -e "${GREEN}✓ Ollama is installed${NC}"
    return 0
}

# Check if Ollama is running
check_ollama_running() {
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${GREEN}✓ Ollama server is running${NC}"
        return 0
    fi
    echo -e "${YELLOW}⚠ Ollama server is not running${NC}"
    echo ""
    echo "Please start Ollama in another terminal:"
    echo "   ollama serve"
    echo ""
    return 1
}

# List models
list_models() {
    local models_file="$SCRIPT_DIR/OLLAMA_MODELS.txt"
    
    if [ ! -f "$models_file" ]; then
        echo -e "${RED}✗ Models file not found: $models_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Models in OLLAMA_MODELS.txt:${NC}"
    echo ""
    
    local count=0
    while IFS= read -r line; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        count=$((count + 1))
        echo -e "  ${GREEN}$count${NC}. $line"
    done < "$models_file"
    
    if [ $count -eq 0 ]; then
        echo -e "  ${YELLOW}No models found in file${NC}"
    fi
    echo ""
}

# Check command
if [ "$COMMAND" = "check" ]; then
    show_banner
    check_ollama
    check_ollama_running
    exit 0
fi

show_banner

# Check Ollama installation
if ! check_ollama; then
    exit 1
fi

# Check Ollama running (optional - don't fail if not running)
check_ollama_running || true

echo ""

# Route to appropriate action
if [ "$COMMAND" = "list" ]; then
    list_models
elif [ "$COMMAND" = "download" ]; then
    if [ -z "$MODEL_NAME" ]; then
        echo -e "${RED}✗ Please specify a model name with --model${NC}"
        echo "Use --help for usage information"
        exit 1
    fi
    echo -e "${BLUE}Downloading model: ${GREEN}$MODEL_NAME${NC}"
    echo ""
    # Use ollama pull directly to show native progress
    ollama pull "$MODEL_NAME"
    echo ""
    echo -e "${GREEN}✓ Model downloaded successfully!${NC}"
else
    # Download all models from file - show native ollama progress
    local models_file="$SCRIPT_DIR/OLLAMA_MODELS.txt"
    
    if [ ! -f "$models_file" ]; then
        echo -e "${RED}✗ Models file not found: $models_file${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Downloading models from OLLAMA_MODELS.txt...${NC}"
    echo ""
    
    # Read models and download each one with native progress
    local count=0
    while IFS= read -r line; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        count=$((count + 1))
        
        echo -e "${BLUE}Downloading ($count): ${GREEN}$line${NC}"
        echo ""
        ollama pull "$line"
        echo ""
        echo -e "${GREEN}✓ $line downloaded${NC}"
        echo "----------------------------------------"
    done < "$models_file"
    
    echo -e "${GREEN}✓ All models downloaded!${NC}"
fi

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        Models ready to use!                    ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
