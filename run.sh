#!/bin/bash
# BitRAG - Quick Run Script
# 
# Usage:
#   ./run.sh [command] [options]
#
# Commands:
#   (none)       Start TUI (default)
#   tui          Start Terminal User Interface
#   cli          Start Command Line Interface
#   status       Show system status
#   logs         View log file
#   clear-logs   Clear log file
#   help         Show this help message
#
# Options:
#   --session <id>   Session ID to use
#   --model <name>   Model to use

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Use virtual environment if exists, otherwise use system python
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

# Show help
show_help() {
    echo -e "${CYAN}BitRAG - 1-bit LLM RAG System${NC}"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo "  (none)       Start TUI (default)"
    echo "  tui          Start Terminal User Interface"
    echo "  cli          Start Command Line Interface"
    echo "  status       Show system status"
    echo "  logs         View log file"
    echo "  clear-logs   Clear log file"
    echo "  help         Show this help message"
    echo ""
    echo -e "${BLUE}Options:${NC}"
    echo "  --session <id>   Session ID to use"
    echo "  --model <name>   Model to use"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  $0                  # Start TUI"
    echo "  $0 tui              # Start TUI"
    echo "  $0 cli              # Start CLI"
    echo "  $0 status           # Show status"
    echo "  $0 tui --session myproject  # Start with custom session"
    echo "  $0 cli --model llama3.2:1b  # Use specific model"
    echo ""
}

# Default command
COMMAND="${1:-tui}"

case "$COMMAND" in
    help|--help|-h)
        show_help
        exit 0
        ;;
    tui)
        echo -e "${GREEN}Starting BitRAG TUI...${NC}"
        # Run the interactive TUI menu
        $PYTHON bitrag.py tui "${@:2}" 2>> "$LOG_FILE"
        ;;
    cli)
        echo -e "${GREEN}Starting BitRAG CLI...${NC}"
        $PYTHON "${SCRIPT_DIR}/src/bitrag/cli/main.py" "${@:2}" 2>> "$LOG_FILE"
        ;;
    status)
        $PYTHON bitrag.py status
        ;;
    interactive)
        echo -e "${GREEN}Starting BitRAG Interactive Mode...${NC}"
        $PYTHON "${SCRIPT_DIR}/src/bitrag/cli/main.py" interactive "${@:2}" 2>> "$LOG_FILE"
        ;;
    logs)
        if [ -f "$LOG_FILE" ]; then
            echo "=== BitRAG Logs ==="
            cat "$LOG_FILE"
        else
            echo -e "${YELLOW}No log file found${NC}"
        fi
        ;;
    clear-logs)
        if [ -f "$LOG_FILE" ]; then
            rm "$LOG_FILE"
            echo -e "${GREEN}Logs cleared${NC}"
        else
            echo -e "${YELLOW}No log file to clear${NC}"
        fi
        ;;
    web)
        echo -e "${GREEN}Starting BitRAG Web UI...${NC}"
        ./run_web.sh "${@:2}"
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo "Run '$0 help' for usage"
        exit 1
        ;;
esac
