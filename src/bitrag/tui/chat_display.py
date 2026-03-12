#!/usr/bin/env python3
"""
BitRAG PyTermGUI - Chat Display Components

Chat display widgets for the BitRAG terminal interface.
Includes thinking widget, model output, and sources display.
"""

from __future__ import annotations

import sys
import os
from typing import Optional, Generator, Callable

# Add src to path for imports
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_SCRIPT_DIR)))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))

import pytermgui as ptg


class UserQueryWidget:
    """Widget for displaying user query."""

    def __init__(self, content: str):
        self.content = content
        self._widget: Optional[ptg.Window] = None

    def create(self) -> ptg.Window:
        """Create the user query widget."""
        self._widget = ptg.Window(
            ptg.Label(f"[green bold]You:[/] {self.content}"),
        )
        return self._widget

    def get_widget(self) -> ptg.Window:
        """Get the widget."""
        if self._widget is None:
            self._widget = self.create()
        return self._widget


class ThinkingWidget:
    """
    Widget for displaying model's reasoning/thinking process.

    Features:
    - Collapsible (can be expanded/collapsed)
    - Shows reasoning steps
    - Supports markdown-like styling
    """

    def __init__(self, thinking: str = ""):
        self.thinking = thinking
        self._widget: Optional[ptg.Window] = None
        self._expanded = True

    def set_thinking(self, thinking: str) -> None:
        """Update thinking content."""
        self.thinking = thinking
        self._widget = None

    def toggle(self) -> None:
        """Toggle expanded/collapsed state."""
        self._expanded = not self._expanded
        self._widget = None

    def create(self) -> ptg.Window:
        """Create the thinking widget."""
        if not self.thinking:
            # Empty thinking - don't show widget
            self._widget = ptg.Window()
            return self._widget

        # Format thinking with markdown-like styling
        lines = self.thinking.split("\n")
        formatted_lines = []

        for line in lines:
            # Add some basic formatting
            if line.strip().startswith("-") or line.strip().startswith("*"):
                formatted_lines.append(f"[dim]{line}[/]")
            elif line.strip().endswith(":"):
                formatted_lines.append(f"[bold]{line}[/]")
            else:
                formatted_lines.append(line)

        content = "\n".join(formatted_lines)

        # Create collapsible section header
        expand_icon = "▼" if self._expanded else "▶"

        self._widget = ptg.Window(
            ptg.Label(f"[yellow bold]{expand_icon} Thinking[/]"),
        )

        if self._expanded:
            self._widget.append(ptg.Label(f"[dim]{content}[/]"))

        return self._widget

    def get_widget(self) -> ptg.Window:
        """Get the widget."""
        if self._widget is None:
            self._widget = self.create()
        return self._widget


class ModelOutputWidget:
    """
    Widget for displaying model response.

    Features:
    - Shows final response text
    - Basic markdown rendering (bold, italic, code blocks)
    """

    def __init__(self, content: str = ""):
        self.content = content
        self._widget: Optional[ptg.Window] = None

    def set_content(self, content: str) -> None:
        """Update content."""
        self.content = content
        self._widget = None

    def append_content(self, chunk: str) -> None:
        """Append a chunk to the content (for streaming)."""
        self.content += chunk
        # Don't recreate widget on each chunk for performance

    def _format_markdown(self, text: str) -> str:
        """Apply basic markdown formatting."""
        # Simple markdown-like formatting
        lines = text.split("\n")
        formatted_lines = []

        for line in lines:
            # Headers
            if line.startswith("### "):
                line = f"[bold]{line[4:]}[/]"
            elif line.startswith("## "):
                line = f"[bold]{line[3:]}[/]"
            elif line.startswith("# "):
                line = f"[bold]{line[2:]}[/]"
            # Bold
            elif "**" in line:
                line = line.replace("**", "[bold]", 1).replace("**", "[/]", 1)
            # Code blocks (inline)
            elif "`" in line:
                line = line.replace("`", "")

            formatted_lines.append(line)

        return "\n".join(formatted_lines)

    def create(self) -> ptg.Window:
        """Create the model output widget."""
        if not self.content:
            self._widget = ptg.Window(
                ptg.Label("[dim]Waiting for response...[/]"),
            )
            return self._widget

        formatted = self._format_markdown(self.content)

        self._widget = ptg.Window(
            ptg.Label(f"[cyan]{formatted}[/]"),
        )
        return self._widget

    def get_widget(self) -> ptg.Window:
        """Get the widget."""
        if self._widget is None:
            self._widget = self.create()
        return self._widget


class SourcesWidget:
    """
    Widget for displaying sources/references.

    Features:
    - Button to show/hide sources
    - Lists referenced documents with excerpts
    """

    def __init__(self, sources: list | None = None, on_show: Callable | None = None):
        self.sources = sources or []
        self.on_show = on_show
        self._widget: Optional[ptg.Window] = None
        self._showing = False

    def set_sources(self, sources: list) -> None:
        """Update sources."""
        self.sources = sources
        self._widget = None

    def toggle(self) -> None:
        """Toggle showing sources."""
        self._showing = not self._showing
        self._widget = None

        if self.on_show:
            self.on_show()

    def create(self) -> ptg.Window:
        """Create the sources widget."""
        if not self.sources:
            self._widget = ptg.Window(
                ptg.Label("[dim]No sources[/]"),
            )
            return self._widget

        # Show/hide toggle button and sources
        icon = "▼" if self._showing else "▶"

        widgets = [
            ptg.Button(f"[{icon} Sources ({len(self.sources)})]", lambda w: self.toggle()),
        ]

        if self._showing:
            widgets.append(ptg.Label(""))
            for i, source in enumerate(self.sources[:5], 1):
                # Get document name
                doc_name = source.get("filename", source.get("file_name", "Unknown"))
                # Get text excerpt
                text = source.get("text", "")[:80]
                if len(source.get("text", "")) > 80:
                    text += "..."

                widgets.append(ptg.Label(f"[dim]  [{i}][/] [yellow]{doc_name}[/]"))
                widgets.append(ptg.Label(f"[dim]      {text}[/]"))

        self._widget = ptg.Window(*widgets)
        return self._widget

    def get_widget(self) -> ptg.Window:
        """Get the widget."""
        if self._widget is None:
            self._widget = self.create()
        return self._widget


class SourcesDialog:
    """
    Dialog for showing full sources list.

    Opens as a modal dialog showing all sources.
    """

    def __init__(self, sources: list | None = None):
        self.sources = sources or []
        self._dialog: Optional[ptg.Window] = None

    def create(self) -> ptg.Window:
        """Create the sources dialog."""
        title = ptg.Label("[bold]Sources Used[/]")

        items = [title, ptg.Label("")]

        for i, source in enumerate(self.sources, 1):
            doc_name = source.get("filename", source.get("file_name", "Unknown"))
            text = source.get("text", "")

            items.append(ptg.Label(f"[bold]{i}.[/] [yellow]{doc_name}[/]"))
            items.append(ptg.Label(f"    [dim]{text}[/]"))
            items.append(ptg.Label(""))

        if not self.sources:
            items.append(ptg.Label("[dim]No sources available[/]"))

        self._dialog = ptg.Window(
            *items,
            box="double",
        )

        return self._dialog

    def get_dialog(self) -> ptg.Window:
        """Get the dialog."""
        if self._dialog is None:
            self._dialog = self.create()
        return self._dialog


class LoadingIndicator:
    """Widget showing loading/processing state."""

    def __init__(self, message: str = "Processing..."):
        self.message = message
        self._widget: Optional[ptg.Window] = None
        self._frame = 0
        self._frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def update(self) -> None:
        """Update animation frame."""
        self._frame = (self._frame + 1) % len(self._frames)

    def create(self) -> ptg.Window:
        """Create the loading widget."""
        icon = self._frames[self._frame]
        self._widget = ptg.Window(
            ptg.Label(f"[yellow]{icon}[/] [dim]{self.message}[/]"),
        )
        return self._widget

    def get_widget(self) -> ptg.Window:
        """Get the widget."""
        return self.create()


class ChatMessage:
    """
    Complete chat message with user query, thinking, model output, and sources.

    Represents a single exchange in the chat.
    """

    def __init__(
        self,
        query: str,
        thinking: str = "",
        response: str = "",
        sources: list | None = None,
    ):
        self.query = query
        self.thinking = thinking
        self.response = response
        self.sources = sources or []
        self._widget: Optional[ptg.Window] = None

    def update_thinking(self, thinking: str) -> None:
        """Update thinking content (for streaming)."""
        self.thinking = thinking
        self._widget = None

    def append_response(self, chunk: str) -> None:
        """Append to response (for streaming)."""
        self.response += chunk

    def set_sources(self, sources: list) -> None:
        """Set sources."""
        self.sources = sources
        self._widget = None

    def create(self) -> ptg.Window:
        """Create the complete message widget."""
        widgets: list[ptg.Widget] = []

        # User query
        widgets.append(ptg.Label(f"[green bold]You:[/] {self.query}"))
        widgets.append(ptg.Label(""))

        # Thinking (if available)
        if self.thinking:
            thinking_widget = ThinkingWidget(self.thinking)
            widgets.append(thinking_widget.get_widget())
            widgets.append(ptg.Label(""))

        # Model response
        if self.response:
            output_widget = ModelOutputWidget(self.response)
            widgets.append(output_widget.get_widget())
            widgets.append(ptg.Label(""))

        # Sources
        if self.sources:
            sources_widget = SourcesWidget(self.sources)
            widgets.append(sources_widget.get_widget())

        self._widget = ptg.Window(*widgets)
        return self._widget

    def get_widget(self) -> ptg.Window:
        """Get the widget."""
        if self._widget is None:
            self._widget = self.create()
        return self._widget


# Export all widgets
__all__ = [
    "UserQueryWidget",
    "ThinkingWidget",
    "ModelOutputWidget",
    "SourcesWidget",
    "SourcesDialog",
    "LoadingIndicator",
    "ChatMessage",
]
