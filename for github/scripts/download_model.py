#!/usr/bin/env python3
"""
BitRAG Model Downloader

Downloads LLM models for BitRAG:
- Ollama models (llama3.2:1b, phi3, etc.)
- BitNet GGUF models from HuggingFace

Usage:
    python scripts/download_model.py --type ollama --model llama3.2:1b
    python scripts/download_model.py --type bitnet
    python scripts/download_model.py --list
"""

import click
import os
import sys
import subprocess
from pathlib import Path

# Colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"  # No Color


def print_banner():
    """Print script banner"""
    print(f"{CYAN}╔════════════════════════════════════════════════════╗{NC}")
    print(f"{CYAN}║        BitRAG Model Downloader                   ║{NC}")
    print(f"{CYAN}╚════════════════════════════════════════════════════╝{NC}")
    print()


# Pre-configured models
OLLAMA_MODELS = {
    "llama3.2:1b": {
        "description": "Fast, reliable - recommended for beginners",
        "size": "~1.3GB",
    },
    "llama3.2:3b": {
        "description": "Better quality, larger model",
        "size": "~1.8GB",
    },
    "phi3:3.8b": {
        "description": "Microsoft Phi-3, good reasoning",
        "size": "~2.3GB",
    },
    "phi3:14b": {
        "description": "Larger Phi-3, best reasoning",
        "size": "~7.9GB",
    },
    "qwen2:0.5b": {
        "description": "Lightest option - ultra fast",
        "size": "~350MB",
    },
    "qwen2:1.5b": {
        "description": "Small but capable",
        "size": "~900MB",
    },
    "tinyllama:1.1b": {
        "description": "Very small, fast",
        "size": "~630MB",
    },
}

BITNET_MODELS = {
    "microsoft/bitnet-b1.58-2B-4T-gguf": {
        "description": "True 1.58-bit model - DEFAULT",
        "size": "~700MB",
        "huggingface_repo": "microsoft/bitnet-b1.58-2B-4T-gguf",
    }
}


@click.command()
@click.option(
    "--type",
    "-t",
    type=click.Choice(["ollama", "bitnet"], case_sensitive=False),
    required=True,
    help="Type of model to download",
)
@click.option("--model", "-m", help="Model name (for Ollama)")
@click.option("--list", "-l", "list_models", is_flag=True, help="List available models")
@click.option("--force", "-f", is_flag=True, help="Force re-download even if model exists")
def download_model(type, model, list_models, force):
    """Download LLM models for BitRAG"""

    print_banner()

    if list_models:
        list_available_models(type)
        return

    if type == "ollama":
        download_ollama_model(model, force)
    elif type == "bitnet":
        download_bitnet_model(force)


def list_available_models(model_type):
    """List available models"""

    if model_type == "ollama":
        print(f"{BLUE}📦 Available Ollama Models:{NC}")
        print()
        for name, info in OLLAMA_MODELS.items():
            print(f"  {GREEN}• {name}{NC}")
            print(f"    Description: {info['description']}")
            print(f"    Size: {info['size']}")
            print()

    elif model_type == "bitnet":
        print(f"{BLUE}📦 Available BitNet Models:{NC}")
        print()
        for name, info in BITNET_MODELS.items():
            print(f"  {GREEN}• {name}{NC}")
            print(f"    Description: {info['description']}")
            print(f"    Size: {info['size']}")
            print()
            print(f"    {YELLOW}⚠️  Note: BitNet requires manual GGUF download from HuggingFace{NC}")


def download_ollama_model(model_name, force):
    """Download model using Ollama"""

    if not model_name:
        print(f"{RED}Error: --model is required for Ollama downloads{NC}")
        print(f"\nAvailable models:")
        for name in OLLAMA_MODELS.keys():
            print(f"  - {name}")
        sys.exit(1)

    # Check if model is valid
    if model_name not in OLLAMA_MODELS:
        print(f"{YELLOW}Warning: '{model_name}' is not in the recommended list{NC}")
        print(f"Will attempt to download anyway...")

    print(f"{BLUE}⬇️  Downloading Ollama model: {GREEN}{model_name}{NC}")
    print(f"   Size: {OLLAMA_MODELS.get(model_name, {}).get('size', 'unknown')}")
    print()

    try:
        # Check if Ollama is installed
        result = subprocess.run(["which", "ollama"], capture_output=True)
        if result.returncode != 0:
            print(f"{RED}Error: Ollama is not installed{NC}")
            print(f"   Install from: https://ollama.com/download")
            sys.exit(1)

        # Check if model already exists
        if not force:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if model_name in result.stdout:
                print(f"{YELLOW}⚠️  Model already exists. Use --force to re-download{NC}")
                return

        # Pull the model
        print(f"{CYAN}Downloading... (this may take a while){NC}")
        result = subprocess.run(["ollama", "pull", model_name], capture_output=True, text=True)

        if result.returncode == 0:
            print()
            print(f"{GREEN}✅ Successfully downloaded: {model_name}{NC}")
        else:
            print(f"{RED}❌ Error downloading model:{NC}")
            print(result.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"{RED}❌ Error: {e}{NC}")
        sys.exit(1)


def download_bitnet_model(force):
    """Download BitNet GGUF model from HuggingFace"""

    print(f"{BLUE}⬇️  Downloading BitNet 1.58 GGUF model{NC}")
    print()

    # Check for HuggingFace Hub
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print(f"{YELLOW}Installing huggingface-hub...{NC}")
        subprocess.run([sys.executable, "-m", "pip", "install", "huggingface-hub"], check=True)
        from huggingface_hub import hf_hub_download

    model_info = BITNET_MODELS["microsoft/bitnet-b1.58-2B-4T-gguf"]
    repo_id = model_info["huggingface_repo"]

    # Determine save directory
    ollama_dir = os.path.expanduser("~/.ollama/models")
    models_dir = os.path.join(ollama_dir, "hub")

    print(f"{CYAN}This will download the BitNet GGUF model...{NC}")
    print(f"{YELLOW}⚠️  Note: After download, you need to create a Modelfile for Ollama{NC}")
    print()

    try:
        # Download the GGUF file
        print(f"{CYAN}Downloading from HuggingFace...{NC}")

        # Get file list from repo
        from huggingface_hub import list_repo_files

        gguf_files = [f for f in list_repo_files(repo_id) if f.endswith(".gguf")]

        if not gguf_files:
            print(f"{RED}No GGUF files found in repository{NC}")
            sys.exit(1)

        print(f"Found GGUF files: {gguf_files}")

        # Download first GGUF file
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=gguf_files[0],
            local_dir=models_dir,
            local_dir_use_symlinks=False,
        )

        print()
        print(f"{GREEN}✅ Downloaded to: {file_path}{NC}")
        print()
        print(f"{YELLOW}Next steps:{NC}")
        print(f"  1. Create a Modelfile for Ollama")
        print(f"  2. Run: ollama create bitnet -f /path/to/Modelfile")
        print(f"  3. Use: bitrag model use bitnet")

    except Exception as e:
        print(f"{RED}❌ Error downloading: {e}{NC}")
        sys.exit(1)


if __name__ == "__main__":
    download_model()
