#!/bin/bash
# BitRAG - Quick Run Script
# Usage: ./run.sh [command] [options]
#
# Commands:
#   (none)    Start TUI (default)
#   tui       Start Terminal User Interface
#   cli       Start Command Line Interface
#   status    Show system status
#   help      Show this help message

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set PYTHONPATH
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"

# Default command
COMMAND="${1:-tui}"

case "$COMMAND" in
    tui)
        echo "Starting BitRAG TUI..."
        exec python bitrag.py tui "${@:2}"
        ;;
    cli)
        echo "Starting BitRAG CLI..."
        exec python bitrag.py cli "${@:2}"
        ;;
    status)
        exec python bitrag.py status
        ;;
    interactive)
        echo "Starting BitRAG Interactive Mode..."
        exec python bitrag.py interactive "${@:2}"
        ;;
    help|--help|-h)
        echo "BitRAG - 1-bit LLM RAG System"
        echo ""
        echo "Usage: ./run.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  (none)     Start TUI (default)"
        echo "  tui        Start Terminal User Interface"
        echo "  cli        Start Command Line Interface"  
        echo "  status     Show system status"
        echo "  help       Show this help message"
        echo ""
        echo "Options:"
        echo "  -s, --session <id>   Session ID (default: default)"
        echo "  -m, --model <name>   Model name"
        echo ""
        echo "Examples:"
        echo "  ./run.sh              # Start TUI"
        echo "  ./run.sh tui          # Start TUI"
        echo "  ./run.sh cli          # Start CLI"
        echo "  ./run.sh status      # Show status"
        echo "  ./run.sh cli -s mysession   # CLI with custom session"
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Run './run.sh help' for usage"
        exit 1
        ;;
esac