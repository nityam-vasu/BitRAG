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

    def run_command(self, command: str = None) -> int:
        """Run a specific command directly."""
        import sys

        # Show minimal banner
        print("\n[BitRAG] Running command...\n")

        # Initialize
        self.initialize()

        if command is None:
            # No command - show help
            self._run_interactive()
            return 0

        command = command.lower()

        # Handle commands
        if command == "status":
            self._show_status()
        elif command == "chat":
            self._quick_chat()
        elif command == "documents":
            self._list_documents()
        elif command == "settings":
            self._show_settings()
        elif command == "upload":
            # Get file path from args
            path = sys.argv[3] if len(sys.argv) > 3 else None
            if path:
                self._upload_document(path)
            else:
                print("Usage: ./run.sh tui upload <file_path>")
        elif command == "query":
            # Get query from args
            query = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else None
            if query:
                self._run_query(query)
            else:
                print("Usage: ./run.sh tui query 'your question'")
        else:
            print(f"Unknown command: {command}")
            print("Available: status, chat, documents, settings, upload, query")

        return 0

    def _quick_chat(self) -> None:
        """Quick chat in non-interactive mode."""
        print("Chat mode - type your question and press Enter")
        print("Press Ctrl+C to exit\n")

        while True:
            try:
                query = input("You: ").strip()
                if query:
                    self._run_query(query)
                    print()
            except KeyboardInterrupt:
                print("\nExiting chat...")
                break

    def _run_query(self, query: str) -> None:
        """Run a query and show results."""
        if self.query_engine is None:
            print("[ERROR] Query engine not initialized")
            return

        if not self._has_documents():
            print("[INFO] No documents indexed. Upload documents first.")
            return

        print("Processing...")
        try:
            result = self.query_engine.query(query)
            response = result.get("response", "No response")
            sources = result.get("sources", [])

            print(f"\nBot: {response}")

            if sources:
                print(f"\nSources ({len(sources)}):")
                for i, src in enumerate(sources[:3], 1):
                    text = src.get("text", "")[:80]
                    print(f"  {i}. {text}...")
        except Exception as e:
            print(f"[ERROR] {e}")

    def _list_documents(self) -> None:
        """List documents."""
        try:
            from bitrag.tui.document_manager import DocumentManager

            doc_manager = DocumentManager(session_id=self.session_id)
            doc_manager.show_list_documents()
        except Exception as e:
            print(f"[ERROR] {e}")

    def _show_settings(self) -> None:
        """Show settings."""
        try:
            from bitrag.tui.settings import SettingsDialogExtended

            settings = SettingsDialogExtended()
            settings.show_full_settings()
        except Exception as e:
            print(f"[ERROR] {e}")

    def _upload_document(self, path: str) -> None:
        """Upload a document."""
        try:
            from bitrag.tui.document_manager import DocumentManager

            doc_manager = DocumentManager(session_id=self.session_id)
            doc_manager.upload_document(path)
        except Exception as e:
            print(f"[ERROR] {e}")

    def run(self, interactive: bool = True) -> None:
        """Run the application."""
        # Show splash screen
        print("\n" + "=" * 50)
        print("  BitRAG - 1-bit LLM RAG System")
        print("  Terminal User Interface")
        print("=" * 50)
        print()

        # Initialize
        self.initialize()

        if interactive:
            # Run interactive menu
            self._run_interactive_menu()
        else:
            # Demo mode
            self._run_demo()

    def _run_interactive_menu(self) -> None:
        """Run interactive menu system."""
        while True:
            print("\n" + "=" * 50)
            print("  BitRAG - Interactive Menu")
            print("=" * 50)
            print()
            print("  1. 💬 Chat - Ask questions about your documents")
            print("  2. 📄 Documents - Manage indexed documents")
            print("  3. ⚙️ Settings - View configuration")
            print("  4. ℹ️ Status - System information")
            print("  5. 🚪 Exit")
            print()

            try:
                choice = input("  Enter choice (1-5): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n  Goodbye! 👋")
                break

            if choice == "1":
                self._interactive_chat()
            elif choice == "2":
                self._interactive_documents_menu()
            elif choice == "3":
                self._interactive_settings()
            elif choice == "4":
                self._interactive_status()
            elif choice == "5":
                print("\n  Goodbye! 👋")
                break
            else:
                print("\n  Invalid choice. Please enter 1-5.")

    def _interactive_documents_menu(self) -> None:
        """Interactive documents menu."""
        from bitrag.tui.document_manager import DocumentManager

        doc_manager = DocumentManager(session_id=self.session_id)

        while True:
            print("\n" + "-" * 50)
            print("  📄 Document Management")
            print("-" * 50)
            print()
            print("  1. 📋 List indexed documents")
            print("  2. 📤 Upload document")
            print("  3. 🗑️ Delete document")
            print("  4. ← Back to main menu")
            print()

            try:
                choice = input("  Enter choice (1-4): ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return

            if choice == "1":
                doc_manager.show_list_documents()
            elif choice == "2":
                print("\n  Enter file path (or type 'browse' to search):")
                try:
                    path = input("  > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    continue

                if path.lower() == "browse":
                    pdfs = doc_manager.ui.browse_pdfs()
                    if pdfs:
                        print(f"\n  Found {len(pdfs)} PDF files:")
                        for i, pdf in enumerate(pdfs[:10], 1):
                            print(f"    {i}. {pdf}")
                        if len(pdfs) > 10:
                            print(f"    ... and {len(pdfs) - 10} more")
                    else:
                        print("\n  No PDF files found in common directories")
                        print("  Try entering full path instead")
                elif path:
                    doc_manager.upload_document(path)
            elif choice == "3":
                doc_manager.show_delete_dialog()
                print("\n  Enter document name/ID to delete (or 'cancel'):")
                try:
                    identifier = input("  > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    continue

                if identifier.lower() != "cancel" and identifier:
                    doc_manager.delete_document(identifier)
            elif choice == "4":
                return

    def _interactive_chat(self) -> None:
        """Interactive chat session."""
        print("\n" + "-" * 50)
        print("  💬 Chat Mode")
        print("-" * 50)
        print("  Type your question and press Enter")
        print("  Type 'exit' or 'quit' to return to menu")
        print()

        if self.query_engine is None:
            print("  [ERROR] Query engine not initialized")
            print("  Check that Ollama is running: ollama serve")
            return

        if not self._has_documents():
            print("  [INFO] No documents indexed yet")
            print("  Upload documents first (Main Menu > Documents)")
            return

        while True:
            try:
                query = input("\n  You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n")
                return

            if not query:
                continue

            if query.lower() in ["exit", "quit", "back"]:
                return

            # Process query
            print("  Processing...")
            try:
                result = self.query_engine.query(query)
                response = result.get("response", "No response")
                sources = result.get("sources", [])

                # Print response
                print(f"\n  Bot: {response[:500]}")
                if len(response) > 500:
                    print("  ...")

                # Print sources
                if sources:
                    print(f"\n  📚 Sources ({len(sources)}):")
                    for i, src in enumerate(sources[:3], 1):
                        text = src.get("text", "")[:60]
                        print(f"    {i}. {text}...")
            except Exception as e:
                print(f"  [ERROR] {e}")

    def _interactive_settings(self) -> None:
        """Show settings."""
        from bitrag.tui.settings import SettingsDialogExtended

        settings = SettingsDialogExtended()
        settings.show_full_settings()

    def _interactive_status(self) -> None:
        """Show system status."""
        print("\n" + "-" * 50)
        print("  ℹ️ System Status")
        print("-" * 50)
        print()

        if self.config:
            print(f"  Model:       {self.config.default_model}")
            print(f"  Ollama URL:  {self.config.ollama_base_url}")
            print(f"  Data Dir:    {self.config.data_dir}")

        # Document count
        doc_count = self._count_documents()
        print(f"  Documents:   {doc_count}")

        # Check Ollama
        import subprocess

        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                model_count = len(lines) - 1 if len(lines) > 1 else 0
                print(f"  Ollama:     Running ({model_count} models)")
            else:
                print("  Ollama:     Not responding")
        except FileNotFoundError:
            print("  Ollama:     Not installed")
        except:
            print("  Ollama:     Not running")

        print()
        print("-" * 50)

    def _has_documents(self) -> bool:
        """Check if there are indexed documents."""
        if self.query_engine is None:
            return False
        try:
            return self.query_engine.has_documents()
        except:
            return False

    def _count_documents(self) -> int:
        """Count indexed documents."""
        if self.query_engine is None:
            return 0
        try:
            return self.query_engine.get_document_count()
        except:
            return 0


def main():
    """Main entry point."""
    app = BitRAGApp()

    # Check for command-line arguments
    import sys

    if len(sys.argv) > 2:
        # Run command mode
        app.run_command(sys.argv[2])
    else:
        # Run interactive
        app.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
