#!/usr/bin/env python3
"""
BitRAG - Download Models from OLLAMA_MODELS.txt

Downloads Ollama models listed in OLLAMA_MODELS.txt one by one.
Shows real-time progress with current model name being downloaded.

Usage:
    python download_model.py              # Download all models
    python download_model.py --model llama3.2:1b  # Download specific model
    python download_model.py --list        # List available models
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
MODELS_FILE = SCRIPT_DIR / "OLLAMA_MODELS.txt"


def print_banner():
    """Print the banner."""
    print()
    print("=" * 60)
    print("  BitRAG - Ollama Model Downloader")
    print("=" * 60)
    print()


def parse_models_file():
    """Parse OLLAMA_MODELS.txt and return list of models."""
    if not MODELS_FILE.exists():
        print(f"❌ Models file not found: {MODELS_FILE}")
        print(f"   Creating default file...")
        create_default_file()
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


def create_default_file():
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


def check_ollama_installed():
    """Check if Ollama CLI is installed."""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ Ollama CLI installed: {version}")
            return True
    except Exception:
        pass

    print("❌ Ollama CLI not found!")
    print()
    print("   Please install Ollama:")
    print("   curl -fsSL https://ollama.com/install.sh | sh")
    print()
    return False


def check_ollama_running():
    """Check if Ollama server is running."""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"], capture_output=True, timeout=5
        )
        if result.returncode == 0:
            print("✓ Ollama server is running")
            return True
    except Exception:
        pass

    print("⚠️  Ollama server is not running")
    print("   Starting Ollama server...")

    # Try to start Ollama
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)

        # Check again
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/tags"], capture_output=True, timeout=5
            )
            if result.returncode == 0:
                print("✓ Ollama server started")
                return True
        except Exception:
            pass

        print("   Please run 'ollama serve' in another terminal")
        return False
    except Exception:
        print("   Could not start Ollama automatically")
        return False


def get_installed_models():
    """Get list of already installed models."""
    installed = set()
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        installed.add(parts[0])
    except Exception:
        pass
    return installed


def download_model(model_name, show_progress=True):
    """
    Download a single model with real-time progress.

    Args:
        model_name: Name of the model to download
        show_progress: Whether to show detailed progress

    Returns:
        True if successful, False otherwise
    """
    model_short = model_name.split(":")[0] if ":" in model_name else model_name

    print()
    print("-" * 60)
    print(f"📥 Downloading: {model_name}")
    print("-" * 60)

    try:
        # Start the download process
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Track progress
        last_update = time.time()
        status_shown = False

        while True:
            # Check if process has finished
            return_code = process.poll()

            if return_code is not None:
                # Process finished
                if return_code == 0:
                    print()
                    print(f"✅ {model_name} downloaded successfully!")
                    return True
                else:
                    stderr = process.stderr.read()
                    print()
                    print(f"❌ Failed to download {model_name}")
                    if stderr:
                        # Show last few lines of error
                        error_lines = stderr.strip().split("\n")[-3:]
                        for line in error_lines:
                            if line.strip():
                                print(f"   {line}")
                    return False

            # Read stdout for progress (non-blocking)
            try:
                import select

                if select.select([process.stdout], [], [], 0.1)[0]:
                    line = process.stdout.readline()
                    if line:
                        if show_progress:
                            # Clean progress output
                            line = line.strip()
                            if line:
                                # Filter useful progress info
                                if (
                                    "%" in line
                                    or "pulling" in line.lower()
                                    or "verifying" in line.lower()
                                ):
                                    print(f"   {line}")
                                    status_shown = True
                                elif len(line) < 100:  # Don't show very long lines
                                    print(f"\r   {line[:60]}...", end="", flush=True)
                                    status_shown = True

                        last_update = time.time()
            except:
                # On Windows or if select not available, just wait
                time.sleep(0.5)

            # Timeout after 30 seconds of no output
            if time.time() - last_update > 30 and not status_shown:
                print()
                print("   (Still downloading...)")
                last_update = time.time()

    except KeyboardInterrupt:
        print()
        print(f"⚠️  Download interrupted by user")
        process.terminate()
        process.wait()
        return False
    except Exception as e:
        print()
        print(f"❌ Error downloading {model_name}: {e}")
        return False


def update_config_default(model_name):
    """Update the default model in config file."""
    try:
        import json

        config_file = SCRIPT_DIR / ".bitrag_config.json"
        config = {}

        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)

        config["default_model"] = model_name
        config["summary_model"] = model_name
        config["tag_model"] = model_name

        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✓ Set {model_name} as default model")

    except Exception as e:
        print(f"⚠️  Could not update config: {e}")


def list_models():
    """List all models in OLLAMA_MODELS.txt."""
    print()
    print("📋 Models in OLLAMA_MODELS.txt:")
    print("-" * 40)

    models = parse_models_file()
    installed = get_installed_models()

    if not models:
        print("   No models found in file")
        return

    for i, model in enumerate(models, 1):
        status = "✅ Installed" if model in installed else "⏳ Not installed"
        status_color = "\033[92m" if model in installed else "\033[93m"
        reset = "\033[0m"
        print(f"   {i}. {model}")
        print(f"      {status_color}{status}{reset}")


def main():
    """Main entry point."""
    print_banner()

    # Parse command line arguments
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "--list" in args:
        list_models()
        return

    # Check Ollama installation
    if not check_ollama_installed():
        sys.exit(1)

    print()

    # Check Ollama server
    if not check_ollama_running():
        print()
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != "y":
            print("Cancelled.")
            sys.exit(0)

    print()

    # Get models to download
    if "--model" in args:
        # Download specific model
        idx = args.index("--model")
        if idx + 1 < len(args):
            models_to_download = [args[idx + 1]]
        else:
            print("❌ Please specify a model name")
            print("   Example: python download_model.py --model llama3.2:1b")
            sys.exit(1)
    else:
        # Download all from file
        models_to_download = parse_models_file()

    if not models_to_download:
        print("❌ No models to download")
        print()
        print("Edit OLLAMA_MODELS.txt to add models")
        sys.exit(1)

    # Get installed models
    print("📦 Checking installed models...")
    installed = get_installed_models()
    print(f"   Found {len(installed)} already installed")
    print()

    # Filter to only download not-installed models
    new_downloads = [m for m in models_to_download if m not in installed]
    skipped = [m for m in models_to_download if m in installed]

    if skipped:
        print("⏭️  Already installed (skipping):")
        for m in skipped:
            print(f"   - {m}")
        print()

    if not new_downloads:
        print("✅ All models are already installed!")
        print()
        if models_to_download:
            update_config_default(models_to_download[0])
        return

    print(f"📥 Downloading {len(new_downloads)} new model(s):")
    for m in new_downloads:
        print(f"   - {m}")
    print()

    # Confirm
    response = input("Start download? (y/n): ").strip().lower()
    if response != "y":
        print("Cancelled.")
        return

    # Download models one by one
    print()
    print("=" * 60)
    print("  Starting Downloads")
    print("=" * 60)

    total = len(new_downloads)
    success = 0
    failed = []

    for i, model in enumerate(new_downloads, 1):
        print()
        print(f"[{i}/{total}] Model {i} of {total}")

        if download_model(model):
            success += 1
        else:
            failed.append(model)

        # Small delay between downloads
        if i < total:
            time.sleep(1)

    # Summary
    print()
    print("=" * 60)
    print("  Download Complete")
    print("=" * 60)
    print()
    print(f"   Total models: {total}")
    print(f"   ✅ Successful: {success}")
    print(f"   ❌ Failed: {len(failed)}")

    if failed:
        print()
        print("   Failed models:")
        for m in failed:
            print(f"   - {m}")

    # Set default model
    if success > 0 and models_to_download:
        print()
        update_config_default(models_to_download[0])

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
