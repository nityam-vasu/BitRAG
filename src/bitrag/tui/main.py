#!/usr/bin/env python3
"""
BitRAG PyTermGUI - Main Application

Terminal-based UI for BitRAG RAG system using PyTermGUI v7.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytermgui as ptg


# Lazy imports for core modules (to avoid import errors during setup)
def _get_indexer(session_id: str):
    """Lazy import of DocumentIndexer."""
    from bitrag.core.indexer import DocumentIndexer

    return DocumentIndexer(session_id)


def _get_config():
    """Lazy import of get_config."""
    from bitrag.core.config import get_config

    return get_config()


class BitRAGApplication:
    """Main PyTermGUI application for BitRAG."""

    def __init__(self):
        self._config = None
        self._session_id = "default"
        self._current_view = "chat"
        self._indexer = None

    @property
    def config(self):
        """Lazy load config."""
        if self._config is None:
            self._config = _get_config()
        return self._config

    @property
    def session_id(self):
        return self._session_id

    @session_id.setter
    def session_id(self, value):
        self._session_id = value
        self._indexer = None  # Reset indexer

    @property
    def indexer(self):
        """Lazy load indexer."""
        if self._indexer is None:
            self._indexer = _get_indexer(self._session_id)
        return self._indexer

    @property
    def current_view(self):
        return self._current_view

    @current_view.setter
    def current_view(self, value):
        self._current_view = value

    def setup(self):
        """Setup the application UI."""
        # Set up aliases for styling
        ptg.aliases["logo"] = "[bold cyan]"
        ptg.aliases["title"] = "[bold light_blue]"
        ptg.aliases["button.ok"] = "[green]"
        ptg.aliases["button.danger"] = "[red]"

    def run(self):
        """Run the application."""
        self.setup()

        # Create the main window
        main_window = ptg.Window(
            self._create_header(),
            "",
            self._create_body(),
            "",
            self._create_footer(),
        )

        # Run the application
        main_window.show()

    def _create_header(self) -> ptg.Label:
        """Create the header."""
        return ptg.Label(
            "[logo]BitRAG[/logo] - [title]1-bit LLM RAG System[/title]",
            align=ptg.HorizontalAlignment.CENTER,
        )

    def _create_body(self) -> ptg.Splitter:
        """Create the main body with sidebar and content."""
        # Create sidebar
        sidebar = ptg.Window(
            "[bold]Navigation[/]",
            "",
            ptg.Button("[green]Chat", self._on_chat_click),
            ptg.Button("[yellow]Documents", self._on_documents_click),
            ptg.Button("[light_blue]Settings", self._on_settings_click),
            "",
            ptg.Button("[green]+ New Session", self._on_new_session),
            "",
            ptg.Button("[red]Exit", self._on_exit),
            width=20,
        )

        # Create main content
        content = self._create_main_content()

        # Use Splitter to combine
        splitter = ptg.Splitter(sidebar, content)

        return splitter

    def _create_main_content(self) -> ptg.Window:
        """Create the main content window."""
        view = self.current_view
        if view == "chat":
            return self._create_chat_view()
        elif view == "documents":
            return self._create_documents_view()
        elif view == "settings":
            return self._create_settings_view()
        return self._create_chat_view()

    def _create_chat_view(self) -> ptg.Window:
        """Create the chat view."""
        return ptg.Window(
            "[bold]Chat View[/] - Ask questions about your documents",
            "",
            "[dim]Upload documents first using the Documents tab[/]",
            "",
            "Type your question below:",
            ptg.InputField(prompt="You: ", placeholder="Ask something..."),
            name="chat",
        )

    def _create_documents_view(self) -> ptg.Window:
        """Create the documents view."""
        return ptg.Window(
            "[bold]Documents[/bold]",
            "",
            ptg.Button("[green]Upload PDF", self._on_upload),
            ptg.Button("[red]Delete", self._on_delete),
            "",
            "[bold]Indexed Documents:[/]",
            "[dim]No documents indexed yet[/]",
            name="documents",
        )

    def _create_settings_view(self) -> ptg.Window:
        """Create the settings view."""
        # Try to get config values, with fallbacks
        try:
            model = self.config.default_model
            embedding = self.config.embedding_model
            ollama_url = self.config.ollama_base_url
        except Exception:
            model = "Not configured"
            embedding = "Not configured"
            ollama_url = "Not configured"

        return ptg.Window(
            "[bold]Settings[/bold]",
            "",
            f"Model: {model}",
            f"Embedding: {embedding}",
            f"Ollama URL: {ollama_url}",
            "",
            ptg.Button("[light_blue]Save Settings", lambda w: None),
            name="settings",
        )

    def _create_footer(self) -> ptg.Label:
        """Create the footer."""
        return ptg.Label(
            "[dim]Ctrl+N: New Chat | Ctrl+D: Documents | Ctrl+S: Settings | Ctrl+Q: Quit[/]",
            align=ptg.HorizontalAlignment.CENTER,
        )

    # Event handlers
    def _on_chat_click(self, widget: ptg.Button) -> None:
        """Handle chat button click."""
        self.current_view = "chat"
        print("Switched to Chat view")

    def _on_documents_click(self, widget: ptg.Button) -> None:
        """Handle documents button click."""
        self.current_view = "documents"
        print("Switched to Documents view")

    def _on_settings_click(self, widget: ptg.Button) -> None:
        """Handle settings button click."""
        self.current_view = "settings"
        print("Switched to Settings view")

    def _on_new_session(self, widget: ptg.Button) -> None:
        """Create a new session."""
        try:
            sessions_dir = self.config.sessions_dir
            if os.path.exists(sessions_dir):
                count = len(
                    [
                        d
                        for d in os.listdir(sessions_dir)
                        if os.path.isdir(os.path.join(sessions_dir, d))
                    ]
                )
                self.session_id = f"session_{count + 1}"
            else:
                self.session_id = "session_1"
            print(f"Created new session: {self.session_id}")
        except Exception as e:
            print(f"Could not create session: {e}")

    def _on_upload(self, widget: ptg.Button) -> None:
        """Handle upload button click."""
        print("Upload - see Plan 07-05")

    def _on_delete(self, widget: ptg.Button) -> None:
        """Handle delete button click."""
        print("Delete - see Plan 07-05")

    def _on_exit(self, widget: ptg.Button) -> None:
        """Handle exit button click."""
        print("\nGoodbye!")
        sys.exit(0)


def main():
    """Main entry point."""
    print("\n[bold cyan]BitRAG PyTermGUI[/bold] - Loading...")
    print("[dim]Note: This is Plan 07-01 - Basic skeleton only\n[/]")

    app = BitRAGApplication()
    app.setup()
    print("[green]PyTermGUI application initialized successfully!")
    print("[dim]Run with: python -m bitrag.tui[/]")


if __name__ == "__main__":
    main()
