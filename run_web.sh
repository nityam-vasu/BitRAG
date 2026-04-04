#!/bin/bash
# BitRAG Web GUI - Run Script
# Starts both the Flask backend and React frontend for BitRAG
#
# Usage:
#   ./run_web.sh                 Start both servers (default: localhost:5000 backend, :5173 frontend)
#   ./run_web.sh --port 8080     Start backend on specific port
#   ./run_web.sh --host 0.0.0.0  Bind to specific host
#   ./run_web.sh --help          Show this help message

set -e

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
PORT=5000
HOST="0.0.0.0"
FRONTEND_PORT=5173
NO_INSTALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "BitRAG Web GUI"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --help, -h              Show this help message"
            echo "  --port, -p <port>       Backend port (default: 5000)"
            echo "  --host, -H <host>       Host to bind to (default: 0.0.0.0)"
            echo "  --frontend-port, -f <port>  Frontend dev server port (default: 5173)"
            echo "  --no-install            Skip dependency installation"
            echo "  --check                 Check system requirements only"
            echo ""
            echo "Examples:"
            echo "  $0                      # Start both servers"
            echo "  $0 --port 8080          # Backend on port 8080"
            echo "  $0 --frontend-port 3000 # Frontend on port 3000"
            exit 0
            ;;
        --port|-p)
            PORT="$2"
            shift 2
            ;;
        --host|-H)
            HOST="$2"
            shift 2
            ;;
        --frontend-port|-f)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        --no-install)
            NO_INSTALL=true
            shift
            ;;
        --check)
            echo "Checking system requirements..."
            echo ""
            
            # Check Python
            if command -v python3 &> /dev/null; then
                python_version=$(python3 --version 2>&1)
                echo -e "${GREEN}✓ Python:${NC} $python_version"
            else
                echo -e "${RED}✗ Python 3 not found${NC}"
            fi
            
            # Check venv
            if [ -d "$SCRIPT_DIR/.venv" ]; then
                echo -e "${GREEN}✓ Virtual environment found${NC}"
            else
                echo -e "${YELLOW}⚠ No virtual environment (will create one)${NC}"
            fi
            
            # Check Ollama
            if command -v ollama &> /dev/null; then
                ollama_version=$(ollama --version 2>&1)
                echo -e "${GREEN}✓ Ollama:${NC} $ollama_version"
            else
                echo -e "${YELLOW}⚠ Ollama not installed${NC}"
            fi
            
            # Check Node.js
            if command -v node &> /dev/null; then
                node_version=$(node --version 2>&1)
                echo -e "${GREEN}✓ Node.js:${NC} $node_version"
            else
                echo -e "${YELLOW}⚠ Node.js not installed${NC}"
            fi
            
            # Check frontend dependencies
            if [ -d "$SCRIPT_DIR/frontend/node_modules" ]; then
                echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
            else
                echo -e "${YELLOW}⚠ Frontend dependencies not installed${NC}"
            fi
            
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        BitRAG Web GUI - Full Stack                  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    if [ ! -z "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    if [ ! -z "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    echo -e "${GREEN}Servers stopped.${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Check if Flask is installed
if ! pip show flask > /dev/null 2>&1; then
    if [ "$NO_INSTALL" = true ]; then
        echo -e "${RED}✗ Flask not installed. Install dependencies first.${NC}"
        exit 1
    fi
    echo -e "${YELLOW}⚠ Installing Python dependencies...${NC}"
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# Check if frontend node_modules exists
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    if [ "$NO_INSTALL" = true ]; then
        echo -e "${RED}✗ Frontend dependencies not installed. Run 'cd frontend && npm install' first.${NC}"
        exit 1
    fi
    echo -e "${YELLOW}⚠ Installing frontend dependencies...${NC}"
    cd "$SCRIPT_DIR/frontend"
    npm install
    cd "$SCRIPT_DIR"
fi

echo ""
echo -e "${GREEN}Starting BitRAG servers...${NC}"
echo ""
echo -e "${BLUE}Backend:${NC}  http://${HOST}:${PORT}"
echo -e "${BLUE}Frontend:${NC} http://${HOST}:${FRONTEND_PORT}"
echo ""

# Start the frontend dev server in the background
echo -e "${YELLOW}Starting frontend dev server...${NC}"
cd "$SCRIPT_DIR/frontend"
FRONTEND_PORT="$FRONTEND_PORT" API_PROXY_TARGET="http://${HOST}:${PORT}" npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if kill -0 "$FRONTEND_PID" 2>/dev/null; then
    echo -e "${GREEN}✓ Frontend dev server running (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}✗ Frontend failed to start. Check /tmp/frontend.log for details.${NC}"
    cat /tmp/frontend.log
    exit 1
fi

# Run the backend Flask app
echo -e "${YELLOW}Starting backend server...${NC}"
cd "$SCRIPT_DIR"
python web_app.py --port "$PORT" --host "$HOST"
