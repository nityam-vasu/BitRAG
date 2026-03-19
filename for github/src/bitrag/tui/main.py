#!/usr/bin/env python3
"""
BitRAG TUI - Main Application

Terminal-based UI for BitRAG RAG system using PyTermGUI.
Run with: python src/bitrag/tui/main.py
"""

import sys
import os

# Add src to path for imports
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_SCRIPT_DIR)))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))


def print_header():
    """Print application header."""
    print("")
    print("=" * 50)
    print("  BitRAG - 1-bit LLM RAG System")
    print("  PyTermGUI Terminal Interface")
    print("=" * 50)
    print("")


def load_config():
    """Load and display configuration."""
    try:
        from bitrag.core.config import get_config

        config = get_config()
        print(f"[OK] Config loaded")
        print(f"     Data dir: {config.data_dir}")
        print(f"     Sessions: {config.sessions_dir}")
        print(f"     Model: {config.default_model}")
        print(f"     Chunk size: {config.chunk_size}")
        print(f"     Top-K: {config.top_k}")
        print("")
        return config
    except Exception as e:
        print(f"[WARN] Could not load config: {e}")
        print("")
        return None


def run_chat_mode(config):
    """Run interactive chat mode."""
    print("\n" + "=" * 50)
    print("  CHAT MODE - Ask questions about your documents")
    print("  Type 'exit' to quit, 'help' for commands")
    print("=" * 50 + "\n")

    # Import query engine
    try:
        from bitrag.core.query import QueryEngine

        query_engine = QueryEngine(config)
        print("[OK] Query engine initialized")
    except Exception as e:
        print(f"[ERROR] Could not initialize query engine: {e}")
        return

    # Chat loop
    while True:
        try:
            user_input = input("\n[You] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break

            if user_input.lower() == "help":
                print_help()
                continue

            if user_input.lower() == "clear":
                print("\n" + "=" * 50)
                print("  CHAT MODE - Ask questions about your documents")
                print("  Type 'exit' to quit, 'help' for commands")
                print("=" * 50 + "\n")
                continue

            # Query the documents
            print("\n[BitRAG] Searching...", end="", flush=True)
            try:
                response = query_engine.query(user_input)
                print(f"\n[BitRAG] {response}")
            except Exception as e:
                print(f"\n[ERROR] Query failed: {e}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            break


def run_documents_mode(config):
    """Run document management mode."""
    print("\n" + "=" * 50)
    print("  DOCUMENTS MODE - Manage indexed PDFs")
    print("  Type 'exit' to quit, 'help' for commands")
    print("=" * 50 + "\n")

    try:
        from bitrag.core.indexer import DocumentIndexer

        indexer = DocumentIndexer("default")
        print("[OK] Document indexer initialized")
    except Exception as e:
        print(f"[ERROR] Could not initialize indexer: {e}")
        return

    print_help_documents()

    # Documents loop
    while True:
        try:
            user_input = input("\n[Documents] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break

            if user_input.lower() == "help":
                print_help_documents()
                continue

            if user_input.lower() == "list":
                list_documents(indexer)
                continue

            # Check if it's a file path to upload
            if os.path.exists(user_input):
                upload_document(indexer, user_input)
                continue

            # Try as command
            parts = user_input.split()
            if len(parts) >= 1:
                cmd = parts[0].lower()
                if cmd == "upload" and len(parts) >= 2:
                    upload_document(indexer, parts[1])
                elif cmd == "delete" and len(parts) >= 2:
                    delete_document(indexer, parts[1])
                else:
                    print(f"[WARN] Unknown command: {cmd}")
                    print_help_documents()
            else:
                print("[WARN] Please enter a command or file path")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            break


def list_documents(indexer):
    """List indexed documents."""
    try:
        docs = indexer.list_documents()
        if not docs:
            print("\n[INFO] No documents indexed yet.")
            return

        print("\n--- Indexed Documents ---")
        for i, doc in enumerate(docs, 1):
            print(f"{i}. {doc.get('filename', 'Unknown')}")
            print(f"   ID: {doc.get('id', 'N/A')[:30]}...")
            print(f"   Chunks: {doc.get('total_chunks', 'N/A')}")
            print(f"   Indexed: {doc.get('indexed_at', 'N/A')}")
            print("")
    except Exception as e:
        print(f"[ERROR] Could not list documents: {e}")


def upload_document(indexer, path):
    """Upload and index a document."""
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return

    print(f"[INFO] Indexing: {path}...")
    try:
        doc_id = indexer.index_document(path, metadata={"source": "tui"})
        print(f"[OK] Document indexed successfully!")
        print(f"     ID: {doc_id}")
    except Exception as e:
        print(f"[ERROR] Could not index document: {e}")


def delete_document(indexer, identifier):
    """Delete a document."""
    try:
        indexer.delete_document(identifier)
        print(f"[OK] Document deleted: {identifier}")
    except Exception as e:
        print(f"[ERROR] Could not delete document: {e}")


def print_help():
    """Print chat mode help."""
    print("""
--- Commands ---
help     - Show this help message
clear    - Clear the screen
exit     - Exit chat mode

--- Tips ---
- Ask questions about your indexed documents
- The system will search and provide AI-generated answers
- Make sure you have indexed documents first!
""")


def print_help_documents():
    """Print documents mode help."""
    print("""
--- Commands ---
list           - List indexed documents
upload <path>  - Upload and index a PDF
delete <id>    - Delete a document by ID or filename
help           - Show this help message
exit           - Exit documents mode

--- Tips ---
- Provide full path to PDF files
- Use 'list' to see indexed documents and their IDs
""")


def run_interactive_menu(config):
    """Run interactive menu for choosing mode."""
    while True:
        print("\n" + "=" * 50)
        print("  BitRAG - Select Mode")
        print("=" * 50)
        print("")
        print("  1. Chat - Ask questions about your documents")
        print("  2. Documents - Manage indexed PDFs")
        print("  3. Settings - View configuration")
        print("  4. Quit")
        print("")

        try:
            choice = input("Select [1-4]: ").strip()

            if choice == "1":
                run_chat_mode(config)
            elif choice == "2":
                run_documents_mode(config)
            elif choice == "3":
                print_settings(config)
            elif choice in ["4", "q", "quit", "exit"]:
                print("\nGoodbye!")
                break
            else:
                print("[WARN] Invalid choice, please try again")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            break


def print_settings(config):
    """Print current settings."""
    if config is None:
        print("\n[ERROR] No configuration loaded")
        return

    print("\n--- Current Settings ---")
    print(f"Data Directory:     {config.data_dir}")
    print(f"Chroma Directory:   {config.chroma_dir}")
    print(f"Sessions Directory: {config.sessions_dir}")
    print(f"Default Model:      {config.default_model}")
    print(f"LLM Type:           {config.llm_type}")
    print(f"Ollama URL:         {config.ollama_base_url}")
    print(f"Chunk Size:         {config.chunk_size}")
    print(f"Chunk Overlap:      {config.chunk_overlap}")
    print(f"Top-K:              {config.top_k}")
    print(f"Collection Name:    {config.collection_name}")
    print("")


def main():
    """Main entry point."""
    print_header()

    # Load configuration
    config = load_config()

    # Check for command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode in ["chat", "c"]:
            run_chat_mode(config)
        elif mode in ["documents", "docs", "d"]:
            run_documents_mode(config)
        elif mode in ["settings", "s"]:
            print_settings(config)
        else:
            run_interactive_menu(config)
    else:
        # Default: run interactive menu
        run_interactive_menu(config)

    return 0


if __name__ == "__main__":
    sys.exit(main())
