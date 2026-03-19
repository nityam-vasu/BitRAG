#!/usr/bin/env python3
"""
BitRAG PyTermGUI - Widgets

Custom TUI widgets for the BitRAG terminal interface.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Callable, Optional

import pytermgui as ptg


class ChatMessage:
    """Represents a single chat message."""

    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_SYSTEM = "system"

    def __init__(
        self,
        content: str,
        role: str = ROLE_USER,
        timestamp: Optional[datetime] = None,
        sources: list | None = None,
    ):
        self.content = content
        self.role = role
        self.timestamp = timestamp or datetime.now()
        self.sources = sources or []

    @property
    def formatted_time(self) -> str:
        """Return formatted timestamp."""
        return self.timestamp.strftime("%H:%M")

    @property
    def is_user(self) -> bool:
        """Check if message is from user."""
        return self.role == self.ROLE_USER

    @property
    def is_assistant(self) -> bool:
        """Check if message is from assistant."""
        return self.role == self.ROLE_ASSISTANT


class ChatDisplay:
    """
    Widget for displaying chat messages.

    Features:
    - Shows user messages with right alignment
    - Shows assistant messages with left alignment
    - Includes timestamps
    - Shows source citations for assistant messages
    - Auto-scroll to bottom on new messages
    """

    def __init__(self):
        self.messages: list[ChatMessage] = []
        self._widget: Optional[ptg.Window] = None

    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the display."""
        self.messages.append(message)
        self._refresh()

    def add_user_message(self, content: str) -> ChatMessage:
        """Add a user message."""
        msg = ChatMessage(content, ChatMessage.ROLE_USER)
        self.add_message(msg)
        return msg

    def add_assistant_message(
        self,
        content: str,
        sources: list | None = None,
    ) -> ChatMessage:
        """Add an assistant message."""
        msg = ChatMessage(
            content,
            ChatMessage.ROLE_ASSISTANT,
            sources=sources,
        )
        self.add_message(msg)
        return msg

    def add_system_message(self, content: str) -> ChatMessage:
        """Add a system message."""
        msg = ChatMessage(content, ChatMessage.ROLE_SYSTEM)
        self.add_message(msg)
        return msg

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        self._refresh()

    def _refresh(self) -> None:
        """Refresh the widget display."""
        if self._widget is not None:
            self._widget = self._create_widget()

    def _create_widget(self) -> ptg.Window:
        """Create the chat display widget."""
        if not self.messages:
            return ptg.Window(
                "[dim]No messages yet. Start a conversation![/]",
                name="chat_display",
            )

        # Build message lines
        lines: list[ptg.Widget] = []

        for msg in self.messages:
            if msg.is_user:
                # User message - right aligned, different color
                lines.append(
                    ptg.Label(
                        f"[dim]{msg.formatted_time}[/] [green]{msg.content}[/]",
                        align=ptg.HorizontalAlignment.RIGHT,
                    )
                )
            elif msg.is_assistant:
                # Assistant message - left aligned with sources
                content_lines = [f"[cyan]{msg.content}[/]"]

                # Add sources if available
                if msg.sources:
                    content_lines.append("")
                    for i, source in enumerate(msg.sources[:3], 1):
                        text = source.get("text", "")[:60]
                        content_lines.append(f"[dim]  [{i}] {text}...[/]")

                lines.append(
                    ptg.Label(
                        "[dim]" + msg.formatted_time + "[/] " + "[cyan]" + msg.content + "[/]",
                        align=ptg.HorizontalAlignment.LEFT,
                    )
                )
            else:
                # System message - centered, dimmed
                lines.append(
                    ptg.Label(
                        f"[dim]{msg.content}[/]",
                        align=ptg.HorizontalAlignment.CENTER,
                    )
                )

        window = ptg.Window(*lines, name="chat_display")
        return window

    def get_widget(self) -> ptg.Window:
        """Get the widget for display."""
        if self._widget is None:
            self._widget = self._create_widget()
        return self._widget

    def __len__(self) -> int:
        """Return number of messages."""
        return len(self.messages)


class InputWidget:
    """
    Widget for user text input.

    Features:
    - Single-line text input
    - Enter key triggers submit callback
    - Escape key clears or cancels
    - Customizable prompt
    """

    def __init__(
        self,
        prompt: str = "You: ",
        placeholder: str = "",
        on_submit: Callable[[str], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ):
        self.prompt = prompt
        self.placeholder = placeholder
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self._widget: Optional[ptg.InputField] = None

    def _create_widget(self) -> ptg.InputField:
        """Create the input field widget."""
        field = ptg.InputField(
            prompt=self.prompt,
            placeholder=self.placeholder,
        )

        # Bind keyboard handlers
        field.bind(
            ptg.Key.ENTER,
            lambda w: self._handle_submit(w),
        )
        field.bind(
            ptg.Key.ESCAPE,
            lambda w: self._handle_cancel(w),
        )

        self._widget = field
        return field

    def _handle_submit(self, widget: ptg.InputField) -> None:
        """Handle submit (Enter key)."""
        text = widget.value
        if text and self.on_submit:
            self.on_submit(text)
        widget.value = ""

    def _handle_cancel(self, widget: ptg.InputField) -> None:
        """Handle cancel (Escape key)."""
        widget.value = ""
        if self.on_cancel:
            self.on_cancel()

    def get_widget(self) -> ptg.InputField:
        """Get the widget for display."""
        if self._widget is None:
            self._widget = self._create_widget()
        return self._widget

    def set_focus(self) -> None:
        """Set focus to this input field."""
        if self._widget:
            self._widget.focus()


class Sidebar:
    """
    Widget for session/conversation list.

    Features:
    - Lists sessions/conversations
    - Shows active session highlight
    - Click to switch sessions
    - Add/delete session buttons
    """

    def __init__(
        self,
        sessions: list[str] | None = None,
        active_session: str = "default",
        on_session_select: Callable[[str], None] | None = None,
        on_new_session: Callable[[], None] | None = None,
        on_delete_session: Callable[[str], None] | None = None,
    ):
        self.sessions = sessions or ["default"]
        self.active_session = active_session
        self.on_session_select = on_session_select
        self.on_new_session = on_new_session
        self.on_delete_session = on_delete_session
        self._widget: Optional[ptg.Window] = None

    def add_session(self, name: str) -> None:
        """Add a new session to the list."""
        if name not in self.sessions:
            self.sessions.append(name)
            self._refresh()

    def remove_session(self, name: str) -> None:
        """Remove a session from the list."""
        if name in self.sessions and name != "default":
            self.sessions.remove(name)
            if self.active_session == name:
                self.active_session = "default"
            self._refresh()

    def set_active_session(self, name: str) -> None:
        """Set the active session."""
        self.active_session = name
        self._refresh()

    def _refresh(self) -> None:
        """Refresh the widget."""
        self._widget = None  # Force recreate

    def _create_widget(self) -> ptg.Window:
        """Create the sidebar widget."""
        # Header
        widgets: list[ptg.Widget] = [
            ptg.Label("[bold]Sessions[/]"),
            ptg.Label(""),
        ]

        # Session buttons
        for session in self.sessions:
            is_active = session == self.active_session
            label = f"[green bold]*[/] {session}" if is_active else f"  {session}"

            btn = ptg.Button(
                label,
                lambda w, s=session: self._handle_session_click(s),
            )
            widgets.append(btn)

        widgets.extend(
            [
                ptg.Label(""),
                ptg.Button(
                    "[green]+ New",
                    lambda w: self._handle_new_session(),
                ),
            ]
        )

        # Add delete button if there are deletable sessions
        if len(self.sessions) > 1:
            widgets.append(
                ptg.Button(
                    "[red]- Delete",
                    lambda w: self._handle_delete_session(),
                )
            )

        window = ptg.Window(*widgets, width=20, name="sidebar")
        self._widget = window
        return window

    def _handle_session_click(self, session: str) -> None:
        """Handle session button click."""
        self.set_active_session(session)
        if self.on_session_select:
            self.on_session_select(session)

    def _handle_new_session(self) -> None:
        """Handle new session button click."""
        if self.on_new_session:
            self.on_new_session()

    def _handle_delete_session(self) -> None:
        """Handle delete session button click."""
        if self.active_session != "default" and self.on_delete_session:
            self.on_delete_session(self.active_session)

    def get_widget(self) -> ptg.Window:
        """Get the widget for display."""
        if self._widget is None:
            self._widget = self._create_widget()
        return self._widget

    def __len__(self) -> int:
        """Return number of sessions."""
        return len(self.sessions)


# Export all widgets
__all__ = [
    "ChatMessage",
    "ChatDisplay",
    "InputWidget",
    "Sidebar",
]
