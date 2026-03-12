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

# Suppress warnings and redirect to log
export PYTHONWARNINGS="ignore::ResourceWarning"
export TRANSFORMERS_NO_ADVISORY_WARNINGS=1
export TF_CPP_MIN_LOG_LEVEL=3
export TRANSFORMERS_VERBOSITY="error"

# Log file
LOG_FILE="${SCRIPT_DIR}/log.txt"

# Default command
COMMAND="${1:-tui}"

case "$COMMAND" in
    tui)
        echo "Starting BitRAG TUI..."
        shift
        $PYTHON bitrag.py tui "$@" 2>> "$LOG_FILE"
        ;;
    cli)
        echo "Starting BitRAG CLI..."
        $PYTHON "${SCRIPT_DIR}/src/bitrag/cli/main.py" "${@:2}" 2>> "$LOG_FILE"
        ;;
    status)
        $PYTHON bitrag.py status
        ;;
    interactive)
        echo "Starting BitRAG Interactive Mode..."
        $PYTHON "${SCRIPT_DIR}/src/bitrag/cli/main.py" interactive "${@:2}" 2>> "$LOG_FILE"
        ;;
    logs)
        if [ -f "$LOG_FILE" ]; then
            echo "=== BitRAG Logs ==="
            cat "$LOG_FILE"
        else
            echo "No log file found"
        fi
        ;;
    clear-logs)
        if [ -f "$LOG_FILE" ]; then
            rm "$LOG_FILE"
            echo "Logs cleared"
        else
            echo "No log file to clear"
        fi
        ;;
    help|--help|-h)
        echo "BitRAG - 1-bit LLM RAG System"
        echo ""
        echo "Usage: ./run.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  (none)      Start TUI (default)"
        echo "  tui         Start Terminal User Interface"
        echo "  cli         Start Command Line Interface"  
        echo "  status      Show system status"
        echo "  logs        View log file"
        echo "  clear-logs  Clear log file"
        echo "  help        Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run.sh              # Start TUI"
        echo "  ./run.sh tui          # Start TUI"
        echo "  ./run.sh cli          # Start CLI"
        echo "  ./run.sh status      # Show status"
        echo "  ./run.sh logs        # View logs"
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Run './run.sh help' for usage"
        exit 1
        ;;
esac