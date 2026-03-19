#!/bin/bash
# BitRAG Flask Web Interface Launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Activate virtual environment
if [ -d "$PROJECT_ROOT/../env_8sem" ]; then
    source "$PROJECT_ROOT/../env_8sem/bin/activate"
elif [ -d "$PROJECT_ROOT/../../env_8sem" ]; then
    source "$PROJECT_ROOT/../../env_8sem/bin/activate"
fi

# Check if Flask-CORS is installed
python3 -c "from flask_cors import CORS" 2>/dev/null || {
    echo "Installing Flask-CORS..."
    pip install flask-cors
}

# Run the Flask application
cd "$SCRIPT_DIR"
python3 app.py
