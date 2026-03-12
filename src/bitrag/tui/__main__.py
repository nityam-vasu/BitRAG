#!/usr/bin/env python3
"""
BitRAG PyTermGUI - Main Entry Point

Entry point for running the TUI application.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main():
    """Main entry point."""
    print("")
    print("=" * 50)
    print("  BitRAG - 1-bit LLM RAG System")
    print("  PyTermGUI Terminal Interface")
    print("=" * 50)
    print("")

    # Try to import and run the app
    try:
        from bitrag.tui.app import BitRAGApp

        # Create and run the app
        app = BitRAGApp()
        app.run()

        print("\n[OK] Application initialized successfully!")
        print("")
        print("Usage:")
        print("  python -m bitrag.tui    - Start the TUI")
        print("")
        print("Keyboard shortcuts:")
        print("  C - Chat")
        print("  S - Settings")
        print("  U - Upload/Documents")
        print("  Q - Quit")
        print("")

    except ImportError as e:
        print(f"[ERROR] Missing dependencies")
        print(f"  {e}")
        print("")
        print("Try: pip install -e .")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
