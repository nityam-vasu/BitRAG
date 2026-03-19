#!/usr/bin/env python3
"""
BitRAG - PyTermGUI Terminal Interface

A proper PyTermGUI-based TUI that renders visual interface.
"""

import sys
import os
import warnings
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Suppress warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

import pytermgui as ptg
from pytermgui import Window, Label, Button, Splitter, InputField, Container


class BitRAGWindow:
    """Main BitRAG Window."""

    def __init__(self):
        self.query_engine = None
        self.config = None
        self.session_id = "default"

    def load_config(self):
        """Load config."""
        try:
            from bitrag.core.config import get_config

            self.config = get_config()
            print(f"[OK] Config loaded: {self.config.default_model}")
        except Exception as e:
            print(f"[WARN] Config: {e}")

    def init_engine(self):
        """Init query engine."""
        try:
            from bitrag.core.query import QueryEngine

            self.query_engine = QueryEngine(
                session_id=self.session_id,
                model=self.config.default_model if self.config else "llama3.2:1b",
            )
            print(f"[OK] Query engine ready")
        except Exception as e:
            print(f"[WARN] Query engine: {e}")

    def create(self) -> Window:
        """Create main window."""

        # Header
        header = Window(
            Label("[bold cyan]BitRAG[/] [dim]- 1-bit LLM RAG System[/]"),
            box="",
        )

        # Chat area
        chat = Window(
            Label("[dim]Welcome to BitRAG![/]"),
            Label(""),
            Label("[dim]Chat with your PDF documents[/]"),
            Label(""),
            Label("[dim]Press 'C' for chat, 'S' for settings, 'U' for upload[/]"),
            box="round",
        )

        # Input area
        self.input_field = InputField(prompt="[green]>[/] ", placeholder="Type your question...")

        input_area = Window(
            Button("[📁 Upload]", lambda w: print("\n[Upload] Use: ./run.sh cli upload <file>")),
            self.input_field,
            Button("[▶ Send]", self.handle_send),
            box="",
        )

        # Footer
        footer = Window(
            Label("[dim]C - Chat  |  S - Settings  |  U - Upload  |  Q - Quit[/]"),
            box="",
        )

        # Main container
        main = Container(
            header,
            chat,
            input_area,
            footer,
        )

        return main

    def handle_send(self, widget=None):
        """Handle send button."""
        query = self.input_field.value
        if query:
            print(f"\n[Query] {query}")
            self.input_field.value = ""


def main():
    """Main entry point."""
    print("\n" + "=" * 50)
    print("  BitRAG - PyTermGUI Terminal Interface")
    print("=" * 50 + "\n")

    # Create window
    window = BitRAGWindow()
    window.load_config()
    window.init_engine()

    # Create app
    app = ptg.WindowManager()
    app.layout = ptg.Layout()
    app.layout.add_slot("body")

    main_window = window.create()
    app.add(main_window)

    # Bind keys
    app.bind("q", lambda _: app.stop())
    app.bind("Q", lambda _: app.stop())
    app.bind("c", lambda w: print("\n[Chat] Start chatting..."))
    app.bind("C", lambda w: print("\n[Chat] Start chatting..."))
    app.bind("s", lambda w: print("\n[Settings] Open settings..."))
    app.bind("S", lambda w: print("\n[Settings] Open settings..."))
    app.bind("u", lambda w: print("\n[Upload] Use: ./run.sh cli upload <file>"))
    app.bind("U", lambda w: print("\n[Upload] Use: ./run.sh cli upload <file>"))

    print("\n[INFO] Starting PyTermGUI...")
    print("[INFO] Press 'q' to quit\n")

    try:
        app.run()
    except Exception as e:
        print(f"[ERROR] {e}")
        print("\n[Fallback] Running in demo mode...")

        # Fallback demo
        print("""
┌──────────────────────────────────────────────┐
│ BitRAG                              ⚙ Settings │
│ 📄 Documents                                   │
├──────────────────────────────────────────────┤
│                                              │
│                Chat Messages                 │
│                                              │
├──────────────────────────────────────────────┤
│ 📁 Upload | [ User Query Input ] | Send ▶     │
└──────────────────────────────────────────────┘

Keyboard shortcuts: 
C -→ Chat    S -→ Settings    U -→ Upload Files    Q -→ Quit
        """)


if __name__ == "__main__":
    main()
