#!/bin/bash
# BitRAG Setup Script for Demo/Showcase
# Run this once to set up the environment

set -e

echo "=========================================="
echo "  BitRAG - Setup for Demo"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -e .

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data chroma_db sessions

# Check Ollama
echo ""
echo "=========================================="
echo "  Checking Ollama..."
echo "=========================================="
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    ollama list || echo "⚠️  Ollama not running - start with: ollama serve"
else
    echo "⚠️  Ollama not found"
    echo "   Install from: https://ollama.ai"
fi

echo ""
echo "=========================================="
echo "  Setup Complete! "
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate: source .venv/bin/activate"
echo "  2. Start Ollama: ollama serve"
echo "  3. Run CLI: bitrag --help"
echo ""
