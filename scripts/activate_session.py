#!/usr/bin/env python3
"""
BitRAG Session Activator + Upload + Index

Activates a session, uploads PDFs, and indexes with real-time progress bar.

Usage:
    python scripts/activate_session.py --session <session_id>
    python scripts/activate_session.py --session <session_id> --upload document.pdf --index
    python scripts/activate_session.py --session <session_id> --list
"""

import click
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bitrag.core.indexer import DocumentIndexer
from bitrag.core.config import get_config

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
    print(f"{CYAN}║     BitRAG Session Activator + Indexer          ║{NC}")
    print(f"{CYAN}╚════════════════════════════════════════════════════╝{NC}")
    print()


class ProgressBar:
    """Custom progress bar with stages"""

    def __init__(self):
        self.stages = [
            "Loading PDF...",
            "Extracting text...",
            "Chunking text...",
            "Creating embeddings...",
            "Storing in vector DB...",
        ]
        self.current_stage = 0
        self.stage_progress = 0

    def update(self, message: str, percentage: int):
        """Update progress bar"""
        # Calculate overall progress
        stage_size = 100 // len(self.stages)
        overall = (self.current_stage * stage_size) + int((percentage / 100) * stage_size)

        # Draw progress bar
        bar_length = 30
        filled = int(bar_length * overall / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"\r  [{bar}] {overall}%  {message}", end="", flush=True)

        if overall >= 100:
            print()

    def next_stage(self, message: str = None):
        """Move to next stage"""
        self.current_stage += 1
        self.stage_progress = 0
        if message:
            self.update(message, 0)


def load_sessions_metadata():
    """Load sessions metadata"""
    import json

    PROJECT_ROOT = Path(__file__).parent.parent
    METADATA_FILE = PROJECT_ROOT / "sessions" / ".sessions_metadata.json"

    if not METADATA_FILE.exists():
        return {"sessions": {}}

    with open(METADATA_FILE, "r") as f:
        return json.load(f)


def check_session_exists(session_id: str) -> bool:
    """Check if session exists"""
    metadata = load_sessions_metadata()
    return session_id in metadata.get("sessions", {})


def list_session_documents(session_id: str) -> list:
    """List documents in a session"""
    config = get_config()
    uploads_dir = config.get_session_uploads_dir(session_id)

    if not uploads_dir.exists():
        return []

    documents = []
    for f in uploads_dir.glob("*.pdf"):
        documents.append(
            {
                "name": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            }
        )

    return documents


@click.command()
@click.option("--session", "-s", required=True, help="Session ID to activate")
@click.option("--upload", "-u", "upload_file", help="PDF file to upload and index")
@click.option("--index", is_flag=True, help="Index the uploaded file")
@click.option("--list", "-l", "list_docs", is_flag=True, help="List documents in session")
def activate_session(session, upload_file, index, list_docs):
    """Activate a session and optionally upload/index documents"""

    print_banner()

    # Check if session exists
    if not check_session_exists(session):
        print(f"{RED}❌ Session not found: {session}{NC}")
        print(f"\n{YELLOW}Hint:{NC} Create a session first:")
        print(f"  python scripts/create_session.py")
        sys.exit(1)

    # Load session info
    metadata = load_sessions_metadata()
    session_info = metadata["sessions"][session]

    print(f"{GREEN}✅ Session activated: {session}{NC}")
    print(f"  Name: {session_info.get('name', 'N/A')}")
    print(f"  Created: {session_info['created_at']}")
    print()

    # List documents
    if list_docs:
        docs = list_session_documents(session)

        if not docs:
            print(f"{YELLOW}No documents uploaded yet.{NC}")
            print(f"\n{YELLOW}Upload a PDF:{NC}")
            print(
                f"  python scripts/activate_session.py --session {session} --upload document.pdf --index"
            )
            return

        print(f"{BLUE}📄 Documents in session:{NC}")
        for doc in docs:
            size_kb = doc["size"] / 1024
            print(f"  • {doc['name']} ({size_kb:.1f} KB)")

        return

    # Upload and index
    if upload_file:
        file_path = Path(upload_file)

        if not file_path.exists():
            print(f"{RED}❌ File not found: {upload_file}{NC}")
            sys.exit(1)

        if file_path.suffix.lower() != ".pdf":
            print(f"{RED}❌ Only PDF files are supported{NC}")
            sys.exit(1)

        print(f"{BLUE}📤 Uploading: {file_path.name}{NC}")

        # Create progress bar
        progress = ProgressBar()

        def progress_callback(message: str, percentage: int):
            progress.update(message, percentage)

        try:
            # Create indexer
            print(f"\n{GREEN}🔄 Indexing document...{NC}")
            indexer = DocumentIndexer(session, progress_callback=progress_callback)

            # Index document
            doc_id = indexer.index_document(str(file_path), metadata={"file_name": file_path.name})

            print(f"\n{GREEN}✅ Successfully indexed: {file_path.name}{NC}")
            print(f"   Document ID: {doc_id}")
            print(f"   Total documents: {indexer.get_document_count()}")

        except Exception as e:
            print(f"\n{RED}❌ Error indexing document: {e}{NC}")
            import traceback

            traceback.print_exc()
            sys.exit(1)

    else:
        # Just activate - show options
        print(f"{YELLOW}Session activated. What would you like to do?{NC}")
        print()
        print(f"  {BLUE}1.{NC} Upload and index a PDF:")
        print(
            f"     python scripts/activate_session.py --session {session} --upload doc.pdf --index"
        )
        print()
        print(f"  {BLUE}2.{NC} List documents:")
        print(f"     python scripts/activate_session.py --session {session} --list")
        print()
        print(f"  {BLUE}3.{NC} Query the documents:")
        print(f'     bitrag query --session {session} "your question"')


if __name__ == "__main__":
    activate_session()
