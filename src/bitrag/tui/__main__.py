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
    print("""
[bold cyan]╔════════════════════════════════════════╗
║                                        ║
║   [bold white]BitRAG[bold cyan] - 1-bit LLM RAG System[bold cyan]    ║
║                                        ║
║        [bold]PyTermGUI Terminal Interface[bold]        ║
║                                        ║
╚════════════════════════════════════════╝
""")

    # Try to import and run the app
    try:
        from bitrag.tui.main import BitRAGApplication

        app = BitRAGApplication()
        app.setup()

        print("[green]Application initialized successfully![/]")
        print("")
        print("[bold]Usage:[/]")
        print("  python -m bitrag.tui    - Start the TUI")
        print("")
        print("[dim]Note: Full TUI requires terminal with mouse support[/]")

    except ImportError as e:
        print(f"[red]Error: Missing dependencies[/]")
        print(f"[dim]{e}[/]")
        print("")
        print("[yellow]Try: pip install -e .[/]")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
