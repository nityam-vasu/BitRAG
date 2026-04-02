#!/usr/bin/env python3
"""
BitRAG Model Downloader

Downloads Ollama models specified in OLLAMA_MODELS.txt.
Skips lines starting with # (comments).
Sets the first non-commented model as default.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
MODELS_FILE = SCRIPT_DIR / "OLLAMA_MODELS.txt"
CONFIG_FILE = SCRIPT_DIR / ".bitrag_config.json"


def parse_models_file():
    """Parse OLLAMA_MODELS.txt and return list of models to download."""
    if not MODELS_FILE.exists():
        print(f"⚠️  Models file not found: {MODELS_FILE}")
        print("   Creating default OLLAMA_MODELS.txt...")
        create_default_models_file()
        return []

    models = []
    with open(MODELS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            models.append(line)

    return models


def create_default_models_file():
    """Create the default OLLAMA_MODELS.txt file."""
    default_content = """# Ollama models for BitRAG
# Edit this file to change which model to use
# First model in the list will be used as default
# Lines starting with # are comments and will be skipped

# Default recommended models
falcon3:1b
llama3.2:1b

# Alternative smaller models (uncomment to use)
#llama3.2:3b
#qwen2.5:0.5b
#qwen2.5:3b

# Additional models (uncomment to download)
gemma3:1b
tinyllama:1.1b
deepseek-r1:1.5b
qwen3:1.7b
granite3.1-moe:1b
qwen3:0.6b
"""
    with open(MODELS_FILE, "w") as f:
        f.write(default_content)


def check_ollama_running():
    """Check if Ollama is running."""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"], capture_output=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def get_installed_models():
    """Get list of already installed models."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            return {line.split()[0] for line in lines if line.strip()}
    except Exception:
        pass
    return set()


def pull_model(model_name, total_models, current_index):
    """Download a single model."""
    print(f"\n📥 [{current_index}/{total_models}] Downloading {model_name}...")
    print("   This may take a few minutes...")

    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        if result.returncode == 0:
            print(f"   ✅ {model_name} downloaded successfully!")
            return True
        else:
            print(f"   ❌ Failed to download {model_name}")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout downloading {model_name}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def update_default_model(model_name):
    """Update the default model in config file."""
    try:
        import json

        config_path = SCRIPT_DIR / ".bitrag_config.json"
        config = {}

        if config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)

        config["default_model"] = model_name
        config["summary_model"] = model_name
        config["tag_model"] = model_name

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"\n   ⚙️  Updated default model to: {model_name}")

    except Exception as e:
        print(f"   ⚠️  Could not update config: {e}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("  BitRAG Model Downloader")
    print("=" * 60)

    # Check if Ollama is installed
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, timeout=5)
    except Exception:
        print("\n❌ Ollama is not installed!")
        print("   Please install Ollama first: https://ollama.com")
        sys.exit(1)

    # Check if Ollama is running
    print("\n🔍 Checking Ollama status...")
    if not check_ollama_running():
        print("\n⚠️  Ollama is not running!")
        print("   Please start Ollama:")
        print("   $ ollama serve")
        print("\n   Or install and start Ollama:")
        print("   $ curl -fsSL https://ollama.com/install.sh | sh")
        print("   $ ollama serve")
        sys.exit(1)

    print("   ✅ Ollama is running!")

    # Parse models file
    print(f"\n📋 Reading models from: {MODELS_FILE}")
    models_to_download = parse_models_file()

    if not models_to_download:
        print("\n⚠️  No models to download found in OLLAMA_MODELS.txt")
        print("   Edit the file to add models.")
        sys.exit(0)

    # Get installed models
    print("\n📦 Checking installed models...")
    installed_models = get_installed_models()
    print(f"   Found {len(installed_models)} already installed")

    # Filter models to download
    models_to_get = [m for m in models_to_download if m not in installed_models]

    if not models_to_get:
        print("\n✅ All models are already installed!")
        print(f"   Default model will be: {models_to_download[0]}")
        update_default_model(models_to_download[0])
        sys.exit(0)

    print(f"\n📥 {len(models_to_get)} models need to be downloaded:")
    for model in models_to_get:
        size_info = get_model_size_estimate(model)
        print(f"   - {model} ({size_info})")

    print("\n" + "=" * 60)
    print("  Starting downloads...")
    print("=" * 60)

    # Download models
    total = len(models_to_get)
    success_count = 0

    for i, model in enumerate(models_to_get, 1):
        print(f"\n[{i}/{total}] {model}")
        if pull_model(model, total, i):
            success_count += 1

    # Summary
    print("\n" + "=" * 60)
    print("  Download Summary")
    print("=" * 60)
    print(f"   Total models: {total}")
    print(f"   Downloaded: {success_count}")
    print(f"   Skipped (already installed): {total - len(models_to_get)}")

    if success_count > 0:
        print(f"\n✅ First model in list set as default: {models_to_download[0]}")
        update_default_model(models_to_download[0])

    print("\n" + "=" * 60)
    print("  Done!")
    print("=" * 60)


def get_model_size_estimate(model_name):
    """Get approximate size for common models."""
    sizes = {
        "falcon3:1b": "~1.2GB",
        "llama3.2:1b": "~1.3GB",
        "llama3.2:3b": "~2.0GB",
        "qwen2.5:0.5b": "~400MB",
        "qwen2.5:3b": "~2.0GB",
        "gemma3:1b": "~800MB",
        "tinyllama:1.1b": "~630MB",
        "deepseek-r1:1.5b": "~1.4GB",
        "qwen3:1.7b": "~1.2GB",
        "qwen3:0.6b": "~500MB",
        "granite3.1-moe:1b": "~700MB",
        "phi3:3.8b": "~2.3GB",
        "phi3:14b": "~7.9GB",
        "mistral:7b": "~4.0GB",
    }
    return sizes.get(model_name, "Unknown size")


if __name__ == "__main__":
    main()
