#!/usr/bin/env python3
"""
BitRAG Session Creator

Creates and manages user sessions for document storage.

Usage:
    python scripts/create_session.py
    python scripts/create_session.py --name my_project
    python scripts/create_session.py --list
    python scripts/create_session.py --delete <session_id>
"""

import click
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def print_banner():
    """Print script banner"""
    print(f"{CYAN}╔════════════════════════════════════════════════════╗{NC}")
    print(f"{CYAN}║        BitRAG Session Manager                  ║{NC}")
    print(f"{CYAN}╚════════════════════════════════════════════════════╝{NC}")
    print()


# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
SESSIONS_DIR = PROJECT_ROOT / "sessions"
METADATA_FILE = SESSIONS_DIR / ".sessions_metadata.json"


def load_sessions_metadata() -> dict:
    """Load sessions metadata"""
    if not METADATA_FILE.exists():
        return {"sessions": {}}

    with open(METADATA_FILE, "r") as f:
        return json.load(f)


def save_sessions_metadata(metadata: dict):
    """Save sessions metadata"""
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)


def create_session_id(name: str = None) -> str:
    """Generate a unique session ID"""
    if name:
        # Use name with timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name.lower().replace(' ', '_')}_{timestamp}"
    else:
        # Use timestamp only
        return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_session(name: str = None) -> dict:
    """Create a new session"""
    session_id = create_session_id(name)

    # Create session directory
    session_dir = SESSIONS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (session_dir / "uploads").mkdir(exist_ok=True)
    (session_dir / "chroma_db").mkdir(exist_ok=True)
    (session_dir / "index").mkdir(exist_ok=True)

    # Create metadata
    metadata = {
        "id": session_id,
        "name": name or session_id,
        "created_at": datetime.now().isoformat(),
        "documents": 0,
    }

    # Save to metadata
    sessions_meta = load_sessions_metadata()
    sessions_meta["sessions"][session_id] = metadata
    save_sessions_metadata(sessions_meta)

    return metadata


def list_sessions() -> list:
    """List all sessions"""
    metadata = load_sessions_metadata()
    sessions = []

    for session_id, data in metadata.get("sessions", {}).items():
        # Check if session directory exists
        session_dir = SESSIONS_DIR / session_id
        if session_dir.exists():
            # Count documents
            uploads_dir = session_dir / "uploads"
            doc_count = len(list(uploads_dir.glob("*.pdf"))) if uploads_dir.exists() else 0
            data["document_count"] = doc_count
            sessions.append(data)

    return sessions


def delete_session(session_id: str) -> bool:
    """Delete a session"""
    # Check if session exists
    metadata = load_sessions_metadata()

    if session_id not in metadata.get("sessions", {}):
        return False

    # Delete directory
    session_dir = SESSIONS_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)

    # Remove from metadata
    del metadata["sessions"][session_id]
    save_sessions_metadata(metadata)

    return True


@click.command()
@click.option("--name", "-n", help="Custom session name")
@click.option("--list", "-l", "list_sessions", is_flag=True, help="List all sessions")
@click.option("--delete", "-d", "delete_session_id", help="Delete a session")
def manage_sessions(name, list_sessions, delete_session_id):
    """Manage BitRAG sessions"""

    print_banner()

    # List sessions
    if list_sessions:
        sessions = list_sessions_func()

        if not sessions:
            print(f"{YELLOW}No sessions found.{NC}")
            return

        print(f"{BLUE}📂 Available Sessions:{NC}")
        print()

        for session in sessions:
            print(f"  {GREEN}• {session['id']}{NC}")
            print(f"    Name: {session.get('name', 'N/A')}")
            print(f"    Created: {session['created_at']}")
            print(f"    Documents: {session.get('document_count', 0)}")
            print()

        return

    # Delete session
    if delete_session_id:
        success = delete_session_func(delete_session_id)

        if success:
            print(f"{GREEN}✅ Session deleted: {delete_session_id}{NC}")
        else:
            print(f"{RED}❌ Session not found: {delete_session_id}{NC}")

        return

    # Create new session
    session = create_session(name)

    print(f"{GREEN}✅ Session created successfully!{NC}")
    print()
    print(f"  {BLUE}Session ID: {GREEN}{session['id']}{NC}")
    print(f"  {BLUE}Name: {GREEN}{session.get('name', 'N/A')}{NC}")
    print(f"  {BLUE}Created: {GREEN}{session['created_at']}{NC}")
    print()
    print(f"{YELLOW}Next steps:{NC}")
    print(f"  1. Activate session: python scripts/activate_session.py --session {session['id']}")
    print(
        f"  2. Upload PDF: python scripts/activate_session.py --session {session['id']} --upload document.pdf --index"
    )
    print()


# Aliases for backward compatibility
def list_sessions_func():
    return list_sessions()


def delete_session_func(session_id: str) -> bool:
    return delete_session(session_id)


if __name__ == "__main__":
    manage_sessions()
