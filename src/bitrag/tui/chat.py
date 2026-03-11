#!/usr/bin/env python3
"""
BitRAG PyTermGUI - Chat Session Management

Handles chat sessions, message history, and persistence.
"""

from __future__ import annotations

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from dataclasses import dataclass, asdict, field


# Lazy imports
def _get_config():
    """Lazy import of get_config."""
    from bitrag.core.config import get_config

    return get_config


@dataclass
class ChatMessageData:
    """Serializable chat message."""

    content: str
    role: str  # "user", "assistant", "system"
    timestamp: str  # ISO format
    sources: list = field(default_factory=list)


@dataclass
class ChatSessionData:
    """Serializable chat session."""

    session_id: str
    title: str
    created_at: str
    updated_at: str
    messages: list = field(default_factory=list)


class ChatSession:
    """
    Manages a single chat session.

    Features:
    - Message history within session
    - Save/load sessions to disk
    - Streaming response handling
    - Session title generation
    """

    def __init__(
        self,
        session_id: str,
        sessions_dir: str | None = None,
    ):
        self.session_id = session_id
        self.sessions_dir = sessions_dir

        # Messages
        self.messages: list[ChatMessageData] = []

        # Metadata
        self.title = f"Chat {session_id}"
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

        # Callbacks
        self.on_message_added: Callable[[ChatMessageData], None] | None = None
        self.on_streaming_chunk: Callable[[str], None] | None = None
        self.on_streaming_complete: Callable[[], None] | None = None

        # Load existing session if available
        self._load()

    @property
    def config(self):
        """Lazy load config."""
        if self.sessions_dir is None:
            return _get_config()
        return None

    @property
    def sessions_path(self) -> Path:
        """Get sessions directory path."""
        if self.sessions_dir:
            return Path(self.sessions_dir)
        try:
            cfg = _get_config()
            return Path(cfg.sessions_dir) / self.session_id
        except Exception:
            return Path(f"./sessions/{self.session_id}")

    def add_message(
        self,
        content: str,
        role: str,
        sources: list | None = None,
    ) -> ChatMessageData:
        """Add a message to the session."""
        msg = ChatMessageData(
            content=content,
            role=role,
            timestamp=datetime.now().isoformat(),
            sources=sources or [],
        )
        self.messages.append(msg)
        self.updated_at = datetime.now().isoformat()

        # Update title if first user message
        if role == "user" and self.title.startswith("Chat "):
            self.title = content[:30] + ("..." if len(content) > 30 else "")

        # Notify callback
        if self.on_message_added:
            self.on_message_added(msg)

        # Save
        self._save()

        return msg

    def add_user_message(self, content: str) -> ChatMessageData:
        """Add a user message."""
        return self.add_message(content, "user")

    def add_assistant_message(
        self,
        content: str,
        sources: list | None = None,
    ) -> ChatMessageData:
        """Add an assistant message."""
        return self.add_message(content, "assistant", sources)

    def add_system_message(self, content: str) -> ChatMessageData:
        """Add a system message."""
        return self.add_message(content, "system")

    def get_messages(self) -> list[ChatMessageData]:
        """Get all messages."""
        return self.messages

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        self._save()

    def _load(self) -> None:
        """Load session from disk."""
        session_file = self.sessions_path / "session.json"
        if session_file.exists():
            try:
                with open(session_file, "r") as f:
                    data = json.load(f)
                    self.title = data.get("title", self.title)
                    self.created_at = data.get("created_at", self.created_at)
                    self.updated_at = data.get("updated_at", self.updated_at)
                    self.messages = [ChatMessageData(**m) for m in data.get("messages", [])]
            except Exception as e:
                print(f"Warning: Could not load session: {e}")

    def _save(self) -> None:
        """Save session to disk."""
        try:
            self.sessions_path.mkdir(parents=True, exist_ok=True)
            session_file = self.sessions_path / "session.json"

            data = {
                "session_id": self.session_id,
                "title": self.title,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "messages": [asdict(m) for m in self.messages],
            }

            with open(session_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save session: {e}")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "message_count": len(self.messages),
        }


class SessionManager:
    """
    Manages multiple chat sessions.

    Features:
    - List all sessions
    - Create new sessions
    - Delete sessions
    - Get/set active session
    """

    def __init__(self, sessions_dir: str | None = None):
        self.sessions_dir = sessions_dir or _get_config().sessions_dir
        self._sessions: dict[str, ChatSession] = {}
        self._active_session_id: str | None = None

    @property
    def active_session(self) -> ChatSession | None:
        """Get the active session."""
        if self._active_session_id and self._active_session_id in self._sessions:
            return self._sessions[self._active_session_id]
        return None

    @property
    def active_session_id(self) -> str:
        """Get active session ID."""
        return self._active_session_id or "default"

    def get_session(self, session_id: str) -> ChatSession:
        """Get or create a session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = ChatSession(
                session_id=session_id,
                sessions_dir=self.sessions_dir,
            )
        return self._sessions[session_id]

    def set_active_session(self, session_id: str) -> None:
        """Set the active session."""
        self._active_session_id = session_id
        # Ensure session exists
        self.get_session(session_id)

    def list_sessions(self) -> list[dict]:
        """List all sessions."""
        sessions_path = Path(self.sessions_dir)
        if not sessions_path.exists():
            return []

        sessions = []
        for item in sessions_path.iterdir():
            if item.is_dir():
                session_file = item / "session.json"
                if session_file.exists():
                    try:
                        with open(session_file, "r") as f:
                            data = json.load(f)
                            sessions.append(
                                {
                                    "session_id": data.get("session_id", item.name),
                                    "title": data.get("title", "Untitled"),
                                    "updated_at": data.get("updated_at", ""),
                                }
                            )
                    except Exception:
                        sessions.append(
                            {
                                "session_id": item.name,
                                "title": item.name,
                                "updated_at": "",
                            }
                        )

        # Sort by updated_at
        sessions.sort(
            key=lambda s: s.get("updated_at", ""),
            reverse=True,
        )
        return sessions

    def create_session(self, title: str | None = None) -> ChatSession:
        """Create a new session."""
        # Generate session ID
        existing = self.list_sessions()
        session_id = f"session_{len(existing) + 1}"

        session = ChatSession(
            session_id=session_id,
            sessions_dir=self.sessions_dir,
        )

        if title:
            session.title = title

        self._sessions[session_id] = session
        self._active_session_id = session_id

        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id == "default":
            return False  # Can't delete default

        try:
            # Remove from memory
            if session_id in self._sessions:
                del self._sessions[session_id]

            # Remove from disk
            session_path = Path(self.sessions_dir) / session_id
            if session_path.exists():
                import shutil

                shutil.rmtree(session_path)

            # Update active if needed
            if self._active_session_id == session_id:
                self._active_session_id = "default"
                self.get_session("default")

            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False


# Export
__all__ = [
    "ChatMessageData",
    "ChatSession",
    "SessionManager",
]
