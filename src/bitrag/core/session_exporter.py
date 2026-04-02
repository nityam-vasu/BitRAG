"""
BitRAG Session Exporter Module

Provides functionality to export chat sessions as TXT files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_session(session_dir: Path) -> Optional[Dict[str, Any]]:
    """Load a session from disk."""
    session_file = session_dir / "session.json"

    if not session_file.exists():
        return None

    try:
        with open(session_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[SessionExporter] Error loading session: {e}")
        return None


def export_session_as_text(session_data: Dict[str, Any], session_id: str) -> str:
    """
    Export a session as formatted text.

    Args:
        session_data: Session data dictionary
        session_id: Session ID

    Returns:
        Formatted text string
    """
    lines = []

    # Header
    lines.append("=" * 50)
    lines.append("BitRAG Chat Export")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"Session: {session_data.get('session_id', session_id)}")
    lines.append(f"Title: {session_data.get('title', 'Untitled Session')}")
    lines.append(f"Created: {session_data.get('created_at', 'Unknown')}")
    lines.append(f"Last Updated: {session_data.get('updated_at', 'Unknown')}")
    lines.append("")

    # Chat history
    lines.append("-" * 50)
    lines.append("Chat History")
    lines.append("-" * 50)
    lines.append("")

    messages = session_data.get("messages", [])

    if not messages:
        lines.append("(No messages in this session)")
    else:
        for msg in messages:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            sources = msg.get("sources", [])

            # Format timestamp
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_time = timestamp
            else:
                formatted_time = ""

            # Role label
            role_label = f"[{role}]"
            if formatted_time:
                role_label += f" {formatted_time}"

            lines.append(role_label)
            lines.append(content)

            # Add sources if present
            if sources:
                lines.append(f"Sources: {', '.join(sources)}")

            lines.append("")

    lines.append("-" * 50)
    lines.append(f"Total messages: {len(messages)}")
    lines.append("")

    return "\n".join(lines)


def list_sessions(sessions_dir: Path) -> List[Dict[str, Any]]:
    """
    List all sessions in the sessions directory.

    Args:
        sessions_dir: Path to sessions directory

    Returns:
        List of session info dictionaries
    """
    if not sessions_dir.exists():
        return []

    sessions = []

    for item in sessions_dir.iterdir():
        if not item.is_dir():
            continue

        session_data = load_session(item)

        if session_data:
            sessions.append(
                {
                    "id": item.name,
                    "title": session_data.get("title", f"Session {item.name}"),
                    "message_count": len(session_data.get("messages", [])),
                    "created_at": session_data.get("created_at", ""),
                    "updated_at": session_data.get("updated_at", ""),
                }
            )
        else:
            # Session exists but no valid JSON
            sessions.append(
                {
                    "id": item.name,
                    "title": f"Session {item.name}",
                    "message_count": 0,
                    "created_at": "",
                    "updated_at": "",
                }
            )

    # Sort by updated_at descending
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)

    return sessions


def delete_session_files(session_dir: Path) -> bool:
    """
    Delete a session directory.

    Args:
        session_dir: Path to session directory

    Returns:
        True if successful, False otherwise
    """
    import shutil

    try:
        if session_dir.exists():
            shutil.rmtree(session_dir)
            return True
        return False
    except Exception as e:
        print(f"[SessionExporter] Error deleting session: {e}")
        return False


def rename_session(session_dir: Path, new_title: str) -> bool:
    """
    Rename a session.

    Args:
        session_dir: Path to session directory
        new_title: New session title

    Returns:
        True if successful, False otherwise
    """
    session_file = session_dir / "session.json"

    if not session_file.exists():
        return False

    try:
        with open(session_file, "r") as f:
            data = json.load(f)

        data["title"] = new_title
        data["updated_at"] = datetime.now().isoformat()

        with open(session_file, "w") as f:
            json.dump(data, f, indent=2)

        return True
    except Exception as e:
        print(f"[SessionExporter] Error renaming session: {e}")
        return False


def create_session(
    sessions_dir: Path, session_id: str, title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new session.

    Args:
        sessions_dir: Path to sessions directory
        session_id: Session ID
        title: Optional session title

    Returns:
        Created session data
    """
    session_dir = sessions_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now().isoformat()
    session_data = {
        "session_id": session_id,
        "title": title or f"Session {session_id}",
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }

    session_file = session_dir / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f, indent=2)

    return session_data
