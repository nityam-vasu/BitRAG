#!/usr/bin/env python3
"""
BitRAG - 1-bit LLM RAG System

Terminal-based RAG application for chatting with your PDF documents.
"""

import sys
import os
import argparse

# Add src to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "src"))


def print_banner():
    """Print ASCII art banner."""
    banner = """
████████  ████ ████████ ████████      ███      ██████
██     ██  ██     ██    ██     ██   ██  ██   ██    ██
██     ██  ██     ██    ██     ██  ██   ██  ██
████████   ██     ██    ████████  ██     ██ ██   ████
██     ██  ██     ██    ██   ██   █████████ ██    ██
██     ██  ██     ██    ██    ██  ██     ██ ██    ██
████████  ████    ██    ██     ██ ██     ██  ██████
    """
    print(banner)
    print("  1-bit LLM RAG System")
    print("  Terminal User Interface")
    print()


def run_tui(args):
    """Run the TUI application."""
    try:
        from bitrag.tui.app import BitRAGApp

        app = BitRAGApp()
        app.run()
        return 0
    except ImportError as e:
        print(f"[ERROR] Missing dependencies: {e}")
        print("\nPlease install required packages:")
        print("  pip install -e .")
        return 1
    except Exception as e:
        print(f"[ERROR] Failed to start TUI: {e}")
        return 1


def run_cli(args):
    """Run the CLI application."""
    try:
        from bitrag.cli.main import cli

        return cli()
    except ImportError as e:
        print(f"[ERROR] Missing dependencies: {e}")
        print("\nPlease install required packages:")
        print("  pip install -e .")
        return 1
    except Exception as e:
        print(f"[ERROR] Failed to start CLI: {e}")
        return 1


def show_status(args):
    """Show system status."""
    try:
        from bitrag.core.config import get_config

        config = get_config()

        print("\n[System Status]")
        print(f"  Data Directory: {config.data_dir}")
        print(f"  ChromaDB:       {config.chroma_dir}")
        print(f"  Sessions:       {config.sessions_dir}")
        print(f"  Default Model:  {config.default_model}")
        print(f"  Ollama URL:     {config.ollama_base_url}")

        # Check Ollama
        import subprocess

        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                model_count = len(lines) - 1
                print(f"  Ollama:         Running ({model_count} models)")
            else:
                print("  Ollama:         Not responding")
        except FileNotFoundError:
            print("  Ollama:         Not installed")
        except Exception:
            print("  Ollama:         Not running")

        print()
        return 0
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BitRAG - Chat with your PDF documents using 1-bit LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bitrag.py                # Start TUI (default)
  bitrag.py tui           # Start Terminal UI
  bitrag.py cli           # Start CLI
  bitrag.py status        # Show system status
  bitrag.py --help        # Show this help

Keyboard Shortcuts (TUI):
  C - Chat screen
  S - Settings
  U - Upload/Documents
  Q - Quit
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # TUI command
    tui_parser = subparsers.add_parser("tui", help="Start Terminal User Interface")
    tui_parser.add_argument("--session", "-s", default="default", help="Session ID")

    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Start Command Line Interface")
    cli_parser.add_argument("--session", "-s", default="default", help="Session ID")
    cli_parser.add_argument("--model", "-m", help="Model to use")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    # Interactive mode (legacy)
    interactive_parser = subparsers.add_parser("interactive", help="Start interactive mode")
    interactive_parser.add_argument("--session", "-s", default="default", help="Session ID")
    interactive_parser.add_argument("--model", "-m", help="Model to use")

    args = parser.parse_args()

    # Default to TUI if no command specified
    if args.command is None:
        print_banner()
        return run_tui(args)

    # Route to appropriate handler
    if args.command == "tui":
        print_banner()
        return run_tui(args)
    elif args.command == "cli":
        return run_cli(args)
    elif args.command == "status":
        return show_status(args)
    elif args.command == "interactive":
        print_banner()
        return run_cli(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
