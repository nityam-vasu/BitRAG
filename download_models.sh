#!/bin/bash
# BitRAG Model Downloader
# Downloads Ollama models specified in OLLAMA_MODELS.txt

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  BitRAG Model Downloader"
echo "=========================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed!"
    echo ""
    echo "Please install Ollama first:"
    echo "   curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "⚠️  Ollama is not running!"
    echo ""
    echo "Please start Ollama in another terminal:"
    echo "   ollama serve"
    echo ""
    read -p "Press Enter to try anyway, or Ctrl+C to exit..."
fi

# Run the Python downloader
python3 "$SCRIPT_DIR/scripts/download_models.py"

echo ""
echo "=========================================="
echo "  Models ready to use!"
echo "=========================================="
