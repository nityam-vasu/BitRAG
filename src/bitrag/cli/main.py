#!/usr/bin/env python3
"""
BitRAG CLI - Enhanced Command-line interface with TUI and /commands
"""

import click
import sys
import os
import subprocess
import warnings
import logging

# Suppress transformers library warnings (BertModel LOAD REPORT)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

# Suppress specific warnings
warnings.filterwarnings("ignore", message=".*position_ids.*")
warnings.filterwarnings("ignore", message=".*BertModel LOAD REPORT.*")
warnings.filterwarnings("ignore", message=".*UNEXPECTED.*")

# Suppress sentence-transformers logging
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bitrag.core.indexer import DocumentIndexer
from bitrag.core.config import get_config


# Colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background
    BG_BLACK = "\033[40m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Light colors
    LIGHT_GRAY = "\033[90m"
    LIGHT_RED = "\033[91m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_YELLOW = "\033[93m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_MAGENTA = "\033[95m"
    LIGHT_CYAN = "\033[96m"


def c(text: str, color: str) -> str:
    """Colorize text"""
    return f"{color}{text}{Colors.RESET}"


def header(text: str) -> str:
    """Bold header"""
    return f"{Colors.BOLD}{text}{Colors.RESET}"


def success(text: str) -> str:
    """Success message"""
    return c(f"✅ {text}", Colors.GREEN)


def error(text: str) -> str:
    """Error message"""
    return c(f"❌ {text}", Colors.RED)


def info(text: str) -> str:
    """Info message"""
    return c(f"ℹ️  {text}", Colors.BLUE)


def warning(text: str) -> str:
    """Warning message"""
    return c(f"⚠️  {text}", Colors.YELLOW)


# ================== TUI Components ==================


def print_banner():
    """Print ASCII banner"""
    banner = f"""
{Colors.CYAN}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   {Colors.BOLD}{Colors.WHITE}  ██╗   ██╗ ██████╗ ██╗██████╗ {Colors.CYAN}                       ║
║   {Colors.BOLD}{Colors.WHITE}  ██║   ██║██╔═══██╗██║██╔══██╗{Colors.CYAN}                      ║
║   {Colors.BOLD}{Colors.WHITE}  ██║   ██║██║   ██║██║██║  ██║{Colors.CYAN}                      ║
║   ╚██╗ ██╔╝██║   ██║██║██║  ██║{Colors.CYAN}                      ║
║    ╚████╔╝ ╚██████╔╝██║██████╔╝{Colors.CYAN}                      ║
║     ╚═══╝   ╚═════╝ ╚═╝╚═════╝ {Colors.CYAN}                       ║
║        {Colors.BOLD}{Colors.WHITE}1-bit LLM RAG System{Colors.CYAN}                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}
"""
    click.echo(banner)


def print_help():
    """Print interactive help"""
    help_text = f"""
{header("📖 Available Commands:")}

  {c("/upload <file>", Colors.CYAN)}     Upload and index a PDF document
  {c("/documents", Colors.CYAN)}          List indexed documents
  {c("/get <name>", Colors.CYAN)}         Get document details
  {c("/delete <name>", Colors.CYAN)}      Delete document by filename
  {c("/browse", Colors.CYAN)}            Browse for PDF files
  {c("/query <text>", Colors.CYAN)}      Query indexed documents  
  {c("/chat", Colors.CYAN)}               Start interactive chat mode
  {c("/model <subcmd>", Colors.CYAN)}    Model management (list|status|use|download)
  {c("/session <subcmd>", Colors.CYAN)}  Session management
  {c("/status", Colors.CYAN)}             Show system status
  {c("/clear", Colors.CYAN)}              Clear screen
  {c("/help", Colors.CYAN)}               Show this help
  {c("/exit", Colors.CYAN)}               Exit interactive mode

{header("💡 Tips:")}
  • Use {c("Tab", Colors.YELLOW)} for auto-complete
  • Use {c("↑↓", Colors.YELLOW)} for command history
  • Use {c("~/Documents/", Colors.YELLOW)} for home directory
  • Commands work without slash too: {c("upload file.pdf", Colors.DIM)}

{header("🚀 Quick Start:")}
  1. {c("/browse", Colors.GREEN)} - Find PDF files
  2. {c("/upload <filename>", Colors.GREEN)} - Upload a document
  3. {c('/query "What is this?"', Colors.GREEN)} - Ask a question
  4. {c("/chat", Colors.GREEN)} - Start chatting
"""
    click.echo(help_text)


def print_status():
    """Print system status"""
    config = get_config()

    # Check Ollama
    ollama_status = "🟢 Running"
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            model_count = len(lines) - 1
            ollama_status = f"🟢 Running ({model_count} models)"
    except:
        ollama_status = "🔴 Not running"

    status = f"""
{header("📊 System Status:")}

  {c("Version:", Colors.DIM)}      0.1.0
  {c("Phase:", Colors.DIM)}        CLI Enhanced
  {c("Ollama:", Colors.DIM)}       {ollama_status}
  {c("Model:", Colors.DIM)}        {config.default_model}
  {c("Embedding:", Colors.DIM)}    {config.embedding_model}

{header("📁 Directories:")}

  {c("Data:", Colors.DIM)}         {config.data_dir}
  {c("ChromaDB:", Colors.DIM)}     {config.chroma_dir}
  {c("Sessions:", Colors.DIM)}      {config.sessions_dir}

"""
    click.echo(status)


# ================== Slash Command Parser ==================

# Try to import readline for arrow key support
try:
    import readline
    import os
    import atexit

    # Enable tab completion with different options
    try:
        readline.parse_and_bind("tab: complete")
    except:
        pass

    try:
        readline.parse_and_bind("bind ^I rl_complete")
    except:
        pass

    readline.set_completer(None)

    # Set up history file
    histfile = os.path.join(os.path.expanduser("~"), ".bitrag_history")
    try:
        readline.read_history_file(histfile)
    except (FileNotFoundError, OSError):
        pass

    # Save history on exit - handle case where history might be empty
    def save_hist():
        try:
            readline.write_history_file(histfile)
        except:
            pass

    atexit.register(save_hist)

    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False


def parse_command(line: str) -> tuple[str, list, dict]:
    """Parse slash command into (command, args, options)"""
    line = line.strip()

    if not line:
        return "", [], {}

    # Add / if not present for known commands
    if not line.startswith("/") and not line.startswith("-"):
        known = ["upload", "query", "chat", "model", "session", "status", "help", "clear", "exit"]
        first_word = line.split()[0] if line.split() else ""
        if first_word in known:
            line = "/" + line

    if not line.startswith("/"):
        # Try as query
        return "query", [line], {}

    # Parse command and arguments (handle quoted strings)
    parts = line[1:].split()
    cmd = parts[0] if parts else ""

    # Reconstruct arguments, handling quoted paths
    args = []
    i = 1
    while i < len(parts):
        part = parts[i]
        # Handle quotes
        if part.startswith('"') and not part.endswith('"'):
            # Find the closing quote
            j = i + 1
            while j < len(parts) and not parts[j].endswith('"'):
                j += 1
            if j < len(parts):
                part = " ".join(parts[i : j + 1])
                j += 1
            else:
                j = i + 1
            i = j
        elif part.startswith("'") and not part.endswith("'"):
            j = i + 1
            while j < len(parts) and not parts[j].endswith("'"):
                j += 1
            if j < len(parts):
                part = " ".join(parts[i : j + 1])
                j += 1
            else:
                j = i + 1
            i = j
        else:
            i += 1

        # Remove surrounding quotes if present
        if len(part) >= 2:
            if (part.startswith('"') and part.endswith('"')) or (
                part.startswith("'") and part.endswith("'")
            ):
                part = part[1:-1]
        args.append(part)

    return cmd, args, {}


# ================== Interactive Mode ==================


def run_interactive(session: str = "default", model: str = None):
    """Run interactive TUI mode"""
    print_banner()
    print_help()

    current_session = session
    current_model = model

    while True:
        try:
            prompt = c(f"\n{Colors.CYAN}bitrag{Colors.RESET}", Colors.BOLD)
            if current_session != "default":
                prompt += c(f"({Colors.BLUE}{current_session}{Colors.CYAN})", Colors.DIM)
            if current_model:
                prompt += c(f" <{Colors.GREEN}{current_model}{Colors.CYAN}>", Colors.DIM)
            prompt += c(" > ", Colors.WHITE)

            line = input(prompt).strip()

            if not line:
                continue

            cmd, args, opts = parse_command(line)

            # Handle commands
            if cmd in ["exit", "quit", "q"]:
                click.echo(c("\n👋 Goodbye!", Colors.YELLOW))
                break

            elif cmd in ["help", "?"]:
                print_help()

            elif cmd in ["clear", "cls"]:
                click.echo("\033[2J\033[H", nl=False)
                print_banner()

            elif cmd in ["status", "stat"]:
                print_status()

            elif cmd == "upload":
                if not args:
                    click.echo(warning("Usage: /upload <file>"))
                    continue
                handle_upload(args[0], current_session)

            elif cmd == "documents":
                handle_documents_list(current_session)

            elif cmd == "get":
                if not args:
                    click.echo(warning("Usage: /get <filename>"))
                    continue
                handle_get_document(args[0], current_session)

            elif cmd == "delete":
                if not args:
                    click.echo(warning("Usage: /delete <filename>"))
                    continue
                handle_delete_document(args[0], current_session)

            elif cmd == "browse":
                handle_browse(current_session)

            elif cmd == "query":
                if not args:
                    click.echo(warning("Usage: /query <question>"))
                    continue
                question = " ".join(args)
                handle_query(question, current_session, current_model)

            elif cmd == "chat":
                handle_chat(current_session, current_model)

            elif cmd == "model":
                if args and args[0] == "list":
                    handle_model_list()
                elif args and args[0] == "status":
                    handle_model_status()
                elif args and args[0] == "use" and len(args) > 1:
                    handle_model_use(args[1])
                elif args and args[0] == "download" and len(args) > 1:
                    handle_model_download(args[1])
                else:
                    click.echo(warning("Usage: /model [list|status|use <name>|download <name>]"))

            elif cmd == "session":
                if args and args[0] == "list":
                    handle_session_list()
                else:
                    click.echo(warning("Usage: /session [list|use <name>]"))

            else:
                click.echo(warning(f"Unknown command: {cmd}. Type /help for available commands."))

        except KeyboardInterrupt:
            click.echo(c("\n\n👋 Interrupted. Type /exit to quit.", Colors.YELLOW))
        except EOFError:
            break


# ================== Command Handlers ==================


def handle_upload(path: str, session: str):
    """Handle upload command"""
    import glob

    # Check if it's a number (selection from browse)
    if path.isdigit():
        # Get list of PDFs again
        home = os.path.expanduser("~")
        search_dirs = [
            os.path.join(home, "Documents"),
            os.path.join(home, "Downloads"),
            os.path.join(home, "Desktop"),
            os.path.join(home, "Documents/PDFs"),
        ]

        pdf_files = []
        for directory in search_dirs:
            if os.path.exists(directory):
                pattern = os.path.join(directory, "*.pdf")
                pdf_files.extend(glob.glob(pattern))

        idx = int(path) - 1
        if 0 <= idx < len(pdf_files):
            path = pdf_files[idx]
        else:
            click.echo(error(f"Invalid number. Use /browse to see available files."))
            return

    # Strip quotes from path
    path = path.strip("'\"")

    # Handle ~ expansion
    if path.startswith("~"):
        path = os.path.expanduser(path)
    else:
        path = os.path.expanduser(path)

    # If still doesn't exist, try current directory
    if not os.path.exists(path):
        # Try as relative path from current directory
        cwd_path = os.path.join(os.getcwd(), path)
        if os.path.exists(cwd_path):
            path = cwd_path

    if not os.path.exists(path):
        click.echo(error(f"File not found: {path}"))
        # Show suggestions
        home = os.path.expanduser("~")
        common_paths = [
            os.path.join(home, "Documents"),
            os.path.join(home, "Downloads"),
            os.path.join(home, "Desktop"),
        ]
        click.echo(f"\n💡 Try using ~/Documents/filename.pdf or check the file exists.")
        click.echo(f"💡 Or use /browse to find files and /upload <number> to select.")
        return

    click.echo(f"📤 Upload: {path}")
    click.echo(f"   Session: {session}")

    try:
        indexer = DocumentIndexer(session)
        doc_id = indexer.index_document(path, metadata={"source": "cli"})
        click.echo(success(f"Indexed: {doc_id}"))
    except Exception as e:
        click.echo(error(f"Failed: {e}"))


def handle_documents_list(session: str):
    """Handle documents list command"""
    try:
        indexer = DocumentIndexer(session)
        docs = indexer.list_documents()

        if not docs:
            click.echo(info("No documents found"))
            return

        click.echo(header(f"\n📚 Documents in session '{session}':"))
        for doc in docs:
            click.echo(f"  • {doc['file_name']} (id: {doc['id'][:20]}...)")
            click.echo(f"    {c('Indexed:', Colors.DIM)} {doc['indexed_at']}")

        click.echo(f"\n💡 Use /get <filename> to view details")
        click.echo(f"💡 Use /delete <filename> to remove a document")

    except Exception as e:
        click.echo(error(str(e)))


def handle_get_document(filename: str, session: str):
    """Handle get document command"""
    try:
        indexer = DocumentIndexer(session)
        doc = indexer.get_document(filename)

        click.echo(header(f"\n📄 Document: {doc['filename']}"))
        click.echo(f"  {c('Total chunks:', Colors.DIM)} {doc['total_chunks']}")

        # Show first few chunks
        click.echo(header("\n📝 Preview:"))
        for i, chunk in enumerate(doc["chunks"][:3], 1):
            text = chunk["text"][:100] + "..." if len(chunk["text"]) > 100 else chunk["text"]
            click.echo(f"  {c(f'Chunk {i}:', Colors.YELLOW)} {text}")

        if doc["total_chunks"] > 3:
            remaining = doc["total_chunks"] - 3
            click.echo(f"  {c(f'... and {remaining} more chunks', Colors.DIM)}")

    except ValueError as e:
        click.echo(error(str(e)))
    except Exception as e:
        click.echo(error(str(e)))


def handle_delete_document(filename: str, session: str):
    """Handle delete document command"""
    try:
        indexer = DocumentIndexer(session)

        # Try to delete by filename first
        try:
            count = indexer.delete_document_by_filename(filename)
            click.echo(success(f"Deleted document '{filename}' and {count} chunks"))
        except ValueError:
            # Fall back to old ID-based deletion
            indexer.delete_document(filename)
            click.echo(success(f"Deleted: {filename}"))

    except Exception as e:
        click.echo(error(str(e)))


def handle_browse(session: str):
    """Browse for PDF files in common locations"""
    import glob

    home = os.path.expanduser("~")
    search_dirs = [
        os.path.join(home, "Documents"),
        os.path.join(home, "Downloads"),
        os.path.join(home, "Desktop"),
        os.path.join(home, "Documents/PDFs"),
    ]

    pdf_files = []
    for directory in search_dirs:
        if os.path.exists(directory):
            pattern = os.path.join(directory, "*.pdf")
            pdf_files.extend(glob.glob(pattern))

    if not pdf_files:
        click.echo(warning("No PDF files found in Documents, Downloads, or Desktop"))
        return

    click.echo(header("📁 Available PDF files:"))
    for i, f in enumerate(pdf_files[:20], 1):  # Show max 20
        filename = os.path.basename(f)
        size = os.path.getsize(f) / 1024  # KB
        click.echo(f"  {c(f'{i}.', Colors.YELLOW)} {filename} ({size:.1f} KB)")

    if len(pdf_files) > 20:
        click.echo(f"  ... and {len(pdf_files) - 20} more")

    click.echo(f"\n💡 To upload: /upload <number> or /upload '<full_path>'")


def handle_query(question: str, session: str, model: str = None):
    """Handle query command"""
    click.echo(f"❓ {question}")
    click.echo(f"   Session: {session}")
    if model:
        click.echo(f"   Model: {model}")

    try:
        from bitrag.core.query import QueryEngine

        engine = QueryEngine(session_id=session, model=model)

        if not engine.has_documents():
            click.echo(error("No documents found. Upload documents first with /upload"))
            return

        click.echo(info("Retrieving context..."))

        result = engine.query(question)

        click.echo(f"\n{header('📖 Sources:')}")
        for i, src in enumerate(result["sources"][:3], 1):
            text = src["text"][:80] + "..." if len(src["text"]) > 80 else src["text"]
            click.echo(f"  {c(f'[{i}]', Colors.YELLOW)} {text}")

        click.echo(f"\n{header('🤖 Answer:')}")
        click.echo(c("─" * 50, Colors.DIM))
        click.echo(result["response"])
        click.echo(c("─" * 50, Colors.DIM))
        click.echo(info(f"Model: {result['model']}"))

    except Exception as e:
        click.echo(error(f"Failed: {e}"))


def handle_chat(session: str, model: str = None):
    """Handle chat command"""
    click.echo(header("\n💬 Chat Mode"))
    click.echo(f"   Session: {session}")
    if model:
        click.echo(f"   Model: {model}")
    click.echo(warning("Type /exit to end chat\n"))

    try:
        from bitrag.core.query import QueryEngine

        engine = QueryEngine(session_id=session, model=model)

        if not engine.has_documents():
            click.echo(error("No documents found. Upload documents first."))
            return

        while True:
            try:
                question = input(c("\nYou: ", Colors.GREEN)).strip()
            except EOFError:
                break

            if question.lower() in ["/exit", "/quit", "exit", "quit"]:
                click.echo(c("👋 Goodbye!", Colors.YELLOW))
                break

            if not question:
                continue

            try:
                click.echo(info("Retrieving..."))
                result = engine.query(question)

                click.echo(f"\n{header('🤖 Answer:')}")
                click.echo(result["response"])

            except Exception as e:
                click.echo(error(f"Error: {e}"))

    except Exception as e:
        click.echo(error(f"Failed: {e}"))


def handle_model_list():
    """Handle model list command"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            click.echo(header("\n📦 Ollama Models:"))
            click.echo(result.stdout)
        else:
            click.echo(error("Failed to list models"))
    except FileNotFoundError:
        click.echo(error("Ollama not found"))
    except Exception as e:
        click.echo(error(f"Error: {e}"))


def handle_model_status():
    """Handle model status command"""
    config = get_config()
    click.echo(header("\n📊 Current Model:"))
    click.echo(f"  {c('Default:', Colors.DIM)} {config.default_model}")
    click.echo(f"  {c('Type:', Colors.DIM)} {config.llm_type}")
    click.echo(f"  {c('Base URL:', Colors.DIM)} {config.ollama_base_url}")


def handle_model_use(model_name: str):
    """Handle model use command"""
    try:
        # Check if model exists in Ollama
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            click.echo(error("Failed to list Ollama models"))
            return

        # Check if the requested model exists
        available_models = result.stdout
        if model_name not in available_models:
            click.echo(warning(f"Model '{model_name}' not found in Ollama"))
            click.echo(info("Run 'ollama pull {model_name}' to download it"))
            return

        # Update config
        config = get_config()
        config.default_model = model_name
        config.save()

        click.echo(success(f"Model changed to: {model_name}"))

    except FileNotFoundError:
        click.echo(error("Ollama not found"))
    except Exception as e:
        click.echo(error(f"Error: {e}"))


def handle_model_download(model_name: str):
    """Handle model download command"""
    try:
        click.echo(f"⬇️  Downloading model: {model_name}")

        # Run ollama pull
        result = subprocess.run(["ollama", "pull", model_name], capture_output=True, text=True)

        if result.returncode == 0:
            click.echo(success(f"Successfully downloaded: {model_name}"))
        else:
            click.echo(error(f"Failed to download: {result.stderr}"))

    except FileNotFoundError:
        click.echo(error("Ollama not found"))
    except Exception as e:
        click.echo(error(f"Error: {e}"))


def handle_session_list():
    """Handle session list command"""
    config = get_config()
    sessions_dir = config.sessions_dir

    if not os.path.exists(sessions_dir):
        click.echo(info("No sessions yet"))
        return

    sessions = [d for d in os.listdir(sessions_dir) if os.path.isdir(os.path.join(sessions_dir, d))]

    if not sessions:
        click.echo(info("No sessions yet"))
    else:
        click.echo(header(f"\n📂 Sessions ({len(sessions)}):"))
        for s in sessions:
            click.echo(f"  • {s}")


# ================== Click CLI ==================


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    BitRAG - Chat with your PDF documents using 1-bit LLM

    Use /commands in interactive mode or standard CLI commands below.
    """
    pass


@cli.command()
@click.option("--session", "-s", default="default", help="Session ID")
@click.option("--model", "-m", help="Model to use")
def interactive(session, model):
    """Start interactive TUI mode"""
    run_interactive(session, model)


# ================== Document Commands ==================


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--session", "-s", default="default", help="Session ID")
def upload(path, session):
    """Upload and index a PDF document"""
    handle_upload(path, session)


@cli.command()
@click.option("--session", "-s", default="default", help="Session ID")
def documents(session):
    """List indexed documents"""
    try:
        indexer = DocumentIndexer(session)
        docs = indexer.list_documents()

        if not docs:
            click.echo(info("No documents found"))
            return

        click.echo(header(f"📚 Documents in session '{session}':"))
        for doc in docs:
            click.echo(f"  • {doc['file_name']} ({doc['id']})")
    except Exception as e:
        click.echo(error(str(e)))


@cli.command()
@click.argument("doc_id")
@click.option("--session", "-s", default="default", help="Session ID")
def delete(doc_id, session):
    """Delete a document by ID (use filename or ID from documents list)"""
    try:
        indexer = DocumentIndexer(session)

        # First check if it's a filename
        try:
            # Try to delete by filename first
            count = indexer.delete_document_by_filename(doc_id)
            click.echo(success(f"Deleted document '{doc_id}' and {count} chunks"))
        except ValueError:
            # Fall back to old ID-based deletion
            indexer.delete_document(doc_id)
            click.echo(success(f"Deleted: {doc_id}"))
    except Exception as e:
        click.echo(error(str(e)))


@cli.command()
@click.argument("filename")
@click.option("--session", "-s", default="default", help="Session ID")
def get_document(filename, session):
    """Get document details by filename"""
    try:
        indexer = DocumentIndexer(session)
        doc = indexer.get_document(filename)

        click.echo(header(f"\n📄 Document: {doc['filename']}"))
        click.echo(f"  {c('Total chunks:', Colors.DIM)} {doc['total_chunks']}")

        # Show first few chunks
        click.echo(header("\n📝 Preview:"))
        for i, chunk in enumerate(doc["chunks"][:3], 1):
            text = chunk["text"][:100] + "..." if len(chunk["text"]) > 100 else chunk["text"]
            click.echo(f"  {c(f'Chunk {i}:', Colors.YELLOW)} {text}")

        if doc["total_chunks"] > 3:
            click.echo(f"  {c(f'... and {doc["total_chunks"] - 3} more chunks', Colors.DIM)}")

    except ValueError as e:
        click.echo(error(str(e)))
    except Exception as e:
        click.echo(error(str(e)))


@cli.command()
@click.argument("filename")
@click.option("--session", "-s", default="default", help="Session ID")
@click.option("--key", "-k", multiple=True, help="Metadata key to update (format: key=value)")
def update_document(filename, session, key):
    """Update document metadata by filename"""
    try:
        # Parse key=value pairs
        metadata = {}
        for kvp in key:
            if "=" in kvp:
                k, v = kvp.split("=", 1)
                metadata[k] = v
            else:
                click.echo(warning(f"Invalid format: {kvp}. Use key=value"))
                return

        if not metadata:
            click.echo(warning("No metadata provided. Use --key key=value"))
            return

        indexer = DocumentIndexer(session)
        indexer.update_document_metadata(filename, metadata)

        click.echo(success(f"Updated metadata for: {filename}"))
        click.echo(f"  {c('New metadata:', Colors.DIM)} {metadata}")

    except ValueError as e:
        click.echo(error(str(e)))
    except Exception as e:
        click.echo(error(str(e)))
    except Exception as e:
        click.echo(error(str(e)))


# ================== Query Commands ==================


@cli.command()
@click.argument("question")
@click.option("--session", "-s", default="default", help="Session ID")
@click.option("--model", "-m", help="Model to use")
def query(question, session, model):
    """Query indexed documents"""
    handle_query(question, session, model)


@cli.command()
@click.option("--session", "-s", default="default", help="Session ID")
@click.option("--model", "-m", help="Model to use")
def chat(session, model):
    """Start interactive chat"""
    handle_chat(session, model)


# ================== Model Commands ==================


@cli.group()
def model():
    """Model management"""
    pass


@model.command(name="list")
def model_list():
    """List available models"""
    handle_model_list()


@model.command(name="status")
def model_status():
    """Show current model"""
    handle_model_status()


@model.command(name="use")
@click.argument("model_name")
def model_use(model_name):
    """Select a model to use"""
    try:
        # Check if model exists in Ollama
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            click.echo(error("Failed to list Ollama models"))
            return

        # Check if the requested model exists
        available_models = result.stdout
        if model_name not in available_models:
            click.echo(warning(f"Model '{model_name}' not found in Ollama"))
            click.echo(info("Run 'ollama pull {model_name}' to download it"))
            return

        # Update config
        config = get_config()
        config.default_model = model_name
        config.save()

        click.echo(success(f"Model changed to: {model_name}"))

    except FileNotFoundError:
        click.echo(error("Ollama not found"))
    except Exception as e:
        click.echo(error(f"Error: {e}"))


@model.command(name="download")
@click.argument("model_name")
def model_download(model_name):
    """Download a model using Ollama"""
    try:
        click.echo(f"⬇️  Downloading model: {model_name}")

        # Run ollama pull
        result = subprocess.run(["ollama", "pull", model_name], capture_output=True, text=True)

        if result.returncode == 0:
            click.echo(success(f"Successfully downloaded: {model_name}"))
        else:
            click.echo(error(f"Failed to download: {result.stderr}"))

    except FileNotFoundError:
        click.echo(error("Ollama not found"))
    except Exception as e:
        click.echo(error(f"Error: {e}"))


# ================== Session Commands ==================


@cli.group()
def session():
    """Session management"""
    pass


@session.command(name="list")
def session_list():
    """List sessions"""
    handle_session_list()


# ================== System Commands ==================


@cli.command()
def status():
    """Show system status"""
    print_status()


if __name__ == "__main__":
    cli()
