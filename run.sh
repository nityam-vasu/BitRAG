#!/bin/bash
# BitRAG - Quick Run Script

# Set PYTHONPATH to include src
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Activate .venv if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check for rlwrap for better terminal support (arrow keys, history)
if command -v rlwrap &> /dev/null; then
    # Run with rlwrap for arrow keys and history
    exec rlwrap -a python -m bitrag.cli.main "$@"
else
    # Run without rlwrap
    exec python -m bitrag.cli.main "$@"
fi
