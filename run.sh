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

# Use virtual environment if exists, otherwise use system python
# Check multiple possible locations
for dir in "$SCRIPT_DIR/../env_8sem" "$SCRIPT_DIR/../../env_8sem" "$SCRIPT_DIR/.venv" ".venv"; do
    if [ -d "$dir" ] && [ -f "$dir/bin/python" ]; then
        PYTHON="$dir/bin/python"
        break
    fi
done

# Fallback to system python
if [ -z "$PYTHON" ] || [ ! -f "$PYTHON" ]; then
    PYTHON="python"
fi

# Set PYTHONPATH
export PYTHONPATH="${SCRIPT_DIR}/src"

# Default command
COMMAND="${1:-tui}"

case "$COMMAND" in
    tui)
        echo "Starting BitRAG TUI..."
        $PYTHON bitrag.py tui "${@:2}"
        ;;
    cli)
        echo "Starting BitRAG CLI..."
        $PYTHON "${SCRIPT_DIR}/src/bitrag/cli/main.py" "${@:2}"
        ;;
    status)
        $PYTHON bitrag.py status
        ;;
    interactive)
        echo "Starting BitRAG Interactive Mode..."
        $PYTHON "${SCRIPT_DIR}/src/bitrag/cli/main.py" interactive "${@:2}"
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
        echo "Examples:"
        echo "  ./run.sh              # Start TUI"
        echo "  ./run.sh tui          # Start TUI"
        echo "  ./run.sh cli          # Start CLI"
        echo "  ./run.sh status      # Show status"
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Run './run.sh help' for usage"
        exit 1
        ;;
esac