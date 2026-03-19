#!/bin/bash
# BitRAG - Quick Install & Run
# Minimal version for demo showcase

set -e

echo "=========================================="
echo "  BitRAG - Demo Setup"
echo "=========================================="

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install in editable mode (may take a few minutes)
echo "[2/4] Installing dependencies (this may take 5-10 minutes)..."
pip install -e .

# Create directories
echo "[3/4] Creating directories..."
mkdir -p data chroma_db sessions

# Check Ollama
echo "[4/4] Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    if pgrep -x "ollama" > /dev/null; then
        echo "✅ Ollama is running"
    else
        echo "⚠️  Ollama not running. Start with: ollama serve"
    fi
else
    echo "⚠️  Ollama not found"
    echo "   Install from: https://ollama.ai"
fi

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate: source venv/bin/activate"
echo "  2. Start Ollama: ollama serve"
echo "  3. Run: bitrag interactive"
echo ""
