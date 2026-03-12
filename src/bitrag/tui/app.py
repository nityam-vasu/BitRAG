#!/usr/bin/env python3
"""
BitRAG PyTermGUI - Main Application

Terminal-based UI for BitRAG RAG system using PyTermGUI.
Implements the TUI specification with splash screen and main window.

Run with: python -m bitrag.tui
"""

from __future__ import annotations

import sys
import os

# Add src to path for imports
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_SCRIPT_DIR)))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))

import pytermgui as ptg
from typing import Optional

# Import chat display widgets
from bitrag.tui.chat_display import (
    ChatMessage,
    ThinkingWidget,
    ModelOutputWidget,
    SourcesWidget,
    SourcesDialog,
    LoadingIndicator,
)


# ASCII Art Banner from specification
BITRAG_BANNER = """
████████  ████ ████████ ████████      ███      ██████
██     ██  ██     ██    ██     ██   ██  ██   ██    ██
██     ██  ██     ██    ██     ██  ██   ██  ██
████████   ██     ██    ████████  ██     ██ ██   ████
██     ██  ██     ██    ██   ██   █████████ ██    ██
██     ██  ██     ██    ██    ██  ██     ██ ██    ██
████████  ████    ██    ██     ██ ██     ██  ██████
"""

# Keyboard shortcuts from specification
KEYBOARD_SHORTCUTS = """
C -→ Chat    S -→ Settings    U -→ Upload Files    Q -→ Quit
"""


class SplashScreen:
    """Splash screen with ASCII art banner."""

    def __init__(self, app: "BitRAGApp"):
        self.app = app
        self._window: Optional[ptg.Window] = None

    def create(self) -> ptg.Window:
        """Create the splash screen window."""
        # Create centered banner
        banner_lines = BITRAG_BANNER.strip().split("\n")

        # Center each line
        max_width = 60
        centered_lines = []
        for line in banner_lines:
            padding = (max_width - len(line)) // 2
            centered_lines.append(" " * padding + line)

        banner = "\n".join(centered_lines)

        self._window = ptg.Window(
            ptg.Label("[bold cyan]" + banner + "[/]"),
            ptg.Label(""),
            ptg.Label("[bold]1-bit LLM RAG System[/]", align=ptg.HorizontalAlignment.CENTER),
            ptg.Label(""),
            ptg.Label("[dim]Initializing...[/]", align=ptg.HorizontalAlignment.CENTER),
        )

        return self._window

    def show(self, terminal: ptg.Terminal) -> None:
        """Show splash screen and handle transition."""
        window = self.create()

        # Get center position
        terminal_width = terminal.width
        terminal_height = terminal.height
        window_width = 70
        window_height = 12

        pos_x = (terminal_width - window_width) // 2
        pos_y = (terminal_height - window_height) // 2

        window.pos = (pos_y, pos_x)

        # Print splash
        print(BITRAG_BANNER)
        print("\n  1-bit LLM RAG System\n")
        print("  Initializing...")

        # Simulate loading
        import time

        time.sleep(0.5)


class HeaderWidget:
    """Header widget showing title, settings, and documents."""

    def __init__(self, app: "BitRAGApp"):
        self.app = app
        self._widget: Optional[ptg.Window] = None

    def create(self) -> ptg.Window:
        """Create header widget."""
        self._widget = ptg.Window(
            ptg.Label("[bold cyan]BitRAG[/]"),
            ptg.Splitter(
                ptg.Label("[dim]│[/]"),
                ptg.Button("[📄 Documents]", lambda w: self.app.show_documents()),
                ptg.Label("[dim]│[/]"),
                ptg.Button("[⚙ Settings]", lambda w: self.app.show_settings()),
            ),
        )
        return self._widget


class SystemResourceWidget:
    """System resource display widget (CPU, Memory, GPU)."""

    def __init__(self):
        self._widget: Optional[ptg.Window] = None

    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        try:
            import psutil

            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0

    def get_memory_usage(self) -> tuple[int, int]:
        """Get memory usage (used, total) in GB."""
        try:
            import psutil

            mem = psutil.virtual_memory()
            return mem.used // (1024**3), mem.total // (1024**3)
        except ImportError:
            return 2, 16

    def get_gpu_usage(self) -> Optional[float]:
        """Get GPU usage percentage."""
        # Try nvidia-smi
        try:
            import subprocess

            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return None

    def create(self) -> ptg.Window:
        """Create resource display widget."""
        cpu = self.get_cpu_usage()
        mem_used, mem_total = self.get_memory_usage()
        gpu = self.get_gpu_usage()

        parts = [f"CPU {cpu:.0f}%", f"Memory {mem_used}GB / {mem_total}GB"]
        if gpu is not None:
            parts.append(f"GPU {gpu:.0f}%")

        resource_text = " | ".join(parts)

        self._widget = ptg.Window(
            ptg.Label(f"[dim]{resource_text}[/]"),
        )
        return self._widget

    def refresh(self) -> None:
        """Refresh resource display."""
        self._widget = None


class ChatAreaWidget:
    """Chat messages display area."""

    def __init__(self, app: "BitRAGApp"):
        self.app = app
        self._widget: Optional[ptg.Window] = None
        self.messages: list[dict] = []

    def add_user_message(self, content: str) -> None:
        """Add a user message."""
        self.messages.append(
            {
                "role": "user",
                "content": content,
            }
        )
        self._refresh()

    def add_assistant_message(self, content: str, sources: list | None = None) -> None:
        """Add an assistant message."""
        self.messages.append(
            {
                "role": "assistant",
                "content": content,
                "sources": sources or [],
            }
        )
        self._refresh()

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        self._refresh()

    def _refresh(self) -> None:
        """Refresh the widget."""
        self._widget = None

    def create(self) -> ptg.Window:
        """Create chat area widget."""
        if not self.messages:
            self._widget = ptg.Window(
                ptg.Label(
                    "[dim]No messages yet. Start a conversation![/]",
                    align=ptg.HorizontalAlignment.CENTER,
                ),
            )
            return self._widget

        lines: list[ptg.Widget] = []

        for msg in self.messages:
            if msg["role"] == "user":
                # User message - right aligned, green
                lines.append(
                    ptg.Label(
                        f"[green]{msg['content']}[/]",
                        align=ptg.HorizontalAlignment.RIGHT,
                    )
                )
            else:
                # Assistant message - left aligned, cyan
                content = f"[cyan]{msg['content']}[/]"

                # Add sources if available
                if msg.get("sources"):
                    sources = msg["sources"]
                    if sources:
                        content += "\n"
                        for i, src in enumerate(sources[:3], 1):
                            text = src.get("text", "")[:60]
                            content += f"\n[dim]  [{i}] {text}...[/]"

                lines.append(
                    ptg.Label(
                        content,
                        align=ptg.HorizontalAlignment.LEFT,
                    )
                )

        self._widget = ptg.Window(
            *lines,
            box="round",
        )
        return self._widget


class ChatBarWidget:
    """Chat input bar with upload, input, and send buttons."""

    def __init__(self, app: "BitRAGApp"):
        self.app = app
        self._widget: Optional[ptg.Splitter] = None
        self._input: Optional[ptg.InputField] = None

    def create(self) -> ptg.Splitter:
        """Create chat bar widget."""
        self._input = ptg.InputField(
            prompt="[green]>[/] ",
            placeholder="Type your question...",
        )

        # Note: In PyTermGUI v7, key binding syntax may differ
        # For demo mode, we'll handle input differently

        self._widget = ptg.Splitter(
            ptg.Button("[📁 Upload]", lambda w: self._handle_upload()),
            ptg.Label(" "),
            self._input,
            ptg.Button("[▶ Send]", lambda w: self._handle_send()),
        )

        return self._widget

    def _handle_send(self) -> None:
        """Handle send button/enter key."""
        # PyTermGUI v7: input.value might need different handling
        try:
            input_value = getattr(self._input, "value", "") or ""
        except:
            input_value = ""

        if input_value:
            query = input_value.strip()
            if query:
                self.app.handle_query(query)
                # Clear input
                try:
                    self._input.value = ""
                except:
                    pass

    def _handle_upload(self) -> None:
        """Handle upload button."""
        self.app.show_documents()


class FooterWidget:
    """Footer widget showing keyboard shortcuts."""

    def __init__(self):
        self._widget: Optional[ptg.Window] = None

    def create(self) -> ptg.Window:
        """Create footer widget."""
        self._widget = ptg.Window(
            ptg.Label(KEYBOARD_SHORTCUTS, align=ptg.HorizontalAlignment.CENTER),
        )
        return self._widget


class BitRAGApp:
    """
    Main BitRAG PyTermGUI Application.

    Implements the TUI specification:
    - Splash screen with ASCII art
    - Main window with header, chat area, chat bar, footer
    - Settings accessible via button/shortcut
    - Document management accessible via button/shortcut
    """

    def __init__(self):
        self.config = None
        self.query_engine = None
        self._manager: Optional[ptg.WindowManager] = None
        self._main_window: Optional[ptg.Window] = None

        # Widgets
        self.splash = SplashScreen(self)
        self.header = HeaderWidget(self)
        self.resources = SystemResourceWidget()
        self.chat_area = ChatAreaWidget(self)
        self.chat_bar = ChatBarWidget(self)
        self.footer = FooterWidget()

        # State
        self.current_view = "chat"  # chat, documents, settings
        self.session_id = "default"

    def load_config(self) -> None:
        """Load configuration and initialize query engine."""
        try:
            from bitrag.core.config import get_config

            self.config = get_config()
            print(f"[OK] Config loaded")
            print(f"     Data dir: {self.config.data_dir}")
            print(f"     Model: {self.config.default_model}")

            # Try to initialize query engine
            self._init_query_engine()

        except Exception as e:
            print(f"[WARN] Could not load config: {e}")

    def _init_query_engine(self) -> None:
        """Initialize the query engine."""
        try:
            from bitrag.core.query import QueryEngine

            self.query_engine = QueryEngine(
                session_id=self.session_id, model=self.config.default_model if self.config else None
            )
            print(f"[OK] Query engine initialized")
            print(f"     Model: {self.query_engine.model}")
        except Exception as e:
            print(f"[WARN] Could not initialize query engine: {e}")
            print(f"     Chat functionality will be limited")

    def initialize(self) -> None:
        """Initialize the application."""
        # Load config
        self.load_config()

        # Initialize PyTermGUI (v7 API)
        # Note: In PyTermGUI v7, theming is done via themes or directly in widgets
        # For now, we skip explicit color definitions to avoid API issues
        try:
            self._manager = ptg.WindowManager()
        except Exception:
            # WindowManager may not work in all terminals
            pass

    def create_main_window(self) -> ptg.Window:
        """Create the main application window."""
        # Create header with title and buttons
        header = self.header.create()

        # Create resource display
        resources = self.resources.create()

        # Create chat area
        chat = self.chat_area.create()

        # Create chat bar
        chat_bar = self.chat_bar.create()

        # Create footer
        footer = self.footer.create()

        # Assemble main window
        self._main_window = ptg.Window(
            # Top row: Header + Resources
            ptg.Splitter(
                header,
                resources,
            ),
            ptg.Label(""),
            # Middle: Chat area (expandable)
            chat,
            ptg.Label(""),
            # Bottom: Chat bar
            chat_bar,
            ptg.Label(""),
            # Footer
            footer,
        )

        return self._main_window

    def run(self) -> None:
        """Run the application."""
        # Show splash screen
        print("\n" + "=" * 50)
        print("  BitRAG - 1-bit LLM RAG System")
        print("  PyTermGUI Terminal Interface")
        print("=" * 50)
        print()

        # Initialize
        self.initialize()

        # Create and show main window
        main_window = self.create_main_window()

        # For now, just print that we're running
        # Full PyTermGUI rendering would require a proper terminal
        print("\n[TUI] Main window created successfully!")
        print("[TUI] Running in demo mode (non-interactive)")
        print()

        # Show the layout structure
        self._print_layout_demo()

    def _print_layout_demo(self) -> None:
        """Print a demo of the layout structure."""
        print("┌──────────────────────────────────────────────┐")
        print("│ BitRAG                              ⚙ Settings │")
        print("│ 📄 Documents                                   │")
        print("├──────────────────────────────────────────────┤")
        print("│                                              │")
        print("│                Chat Messages                 │")
        print("│                                              │")
        print("├──────────────────────────────────────────────┤")
        print("│ 📁 Upload | [ User Query Input ] | Send ▶     │")
        print("└──────────────────────────────────────────────┘")
        print()
        print("Keyboard shortcuts:", KEYBOARD_SHORTCUTS)
        print()

    def handle_query(self, query: str) -> None:
        """Handle a user query with RAG integration."""
        print(f"\n[Query] {query}")

        # Add user message to chat
        self.chat_area.add_user_message(query)

        # Check if query engine is available
        if self.query_engine is None:
            print("[BitRAG] Query engine not available")
            response = "Query engine not initialized. Please check your configuration."
            sources = []
            self.chat_area.add_assistant_message(response, sources)
            return

        # Show "thinking" message
        print("[BitRAG] Searching documents...")

        try:
            # Check if there are documents indexed
            if not self.query_engine.has_documents():
                print("[BitRAG] No documents found")
                response = "No documents found in the index. Please upload documents first using the Documents panel."
                sources = []
                self.chat_area.add_assistant_message(response, sources)
                return

            # Use streaming for better UX
            print("[BitRAG] Generating response...")

            # For demo mode, we'll use the non-streaming query
            # In full mode, would use query_engine.query_streaming()
            result = self.query_engine.query(query)

            response = result.get("response", "")
            sources = result.get("sources", [])

            # Add assistant response with sources
            self.chat_area.add_assistant_message(response, sources)

            print(f"[BitRAG] Response received ({len(sources)} sources)")

            # Print sources for demo
            if sources:
                print("\n[Sources]")
                for i, src in enumerate(sources[:3], 1):
                    text = src.get("text", "")[:80]
                    print(f"  [{i}] {text}...")

        except Exception as e:
            print(f"[ERROR] Query failed: {e}")
            response = f"Error processing query: {str(e)}"
            sources = []
            self.chat_area.add_assistant_message(response, sources)

    def show_settings(self) -> None:
        """Show settings dialog."""
        print("\n[BitRAG] Opening Settings...")

        # Import settings components
        try:
            from bitrag.tui.settings import SettingsDialogExtended

            # Create settings dialog with callbacks
            settings_dialog = SettingsDialogExtended(on_show_documents=self.show_documents)

            # Show full settings
            settings_dialog.show_full_settings()

        except Exception as e:
            print(f"[ERROR] Could not load settings: {e}")
            # Fallback to basic settings
            print("\n[BitRAG] Settings")
            print("  - Ollama Port Configuration")
            print("  - Model Selection")
            print("  - Model Download/Delete")
            print("  - Dual Model Mode")
            print("  - Hybrid Retrieval Slider")
            print("  - Document Management")

        print()

    def show_documents(self) -> None:
        """Show document management."""
        print("\n[BitRAG] Opening Document Management...")
        print("  - List Documents")
        print("  - Upload Document")
        print("  - Delete Document")
        print()
        # Note: Full document management would be implemented in 08-04


def main():
    """Main entry point."""
    app = BitRAGApp()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
