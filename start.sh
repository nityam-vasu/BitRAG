#!/bin/bash

# BitRAG Startup Script
# Starts Ollama (optional), backend first, then frontend

echo "=========================================="
echo "         Starting BitRAG..."
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Kill any existing processes on ports 5000 and 5173
echo "[1/4] Checking for existing processes..."
lsof -ti:5000 | xargs -r kill -9 2>/dev/null
lsof -ti:5173 | xargs -r kill -9 2>/dev/null
lsof -ti:5174 | xargs -r kill -9 2>/dev/null
echo "      Done."

# Check/Start Ollama
echo "[2/4] Checking Ollama..."
if pgrep -x "ollama" > /dev/null; then
    echo "      Ollama already running"
else
    echo "      Starting Ollama..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
fi

# Start backend in background
echo "[3/4] Starting backend (port 5000)..."
cd "$SCRIPT_DIR"
python web_app.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "      Waiting for backend to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:5000/api/status > /dev/null 2>&1; then
        echo "      Backend ready!"
        break
    fi
    sleep 1
done

# Start frontend
echo "[4/4] Starting frontend (port 5173)..."
cd "$SCRIPT_DIR/frontend"
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "      Waiting for frontend to initialize..."
sleep 3

# Get the IP address
IP_ADDR=$(hostname -I | awk '{print $1}')

echo ""
echo "=========================================="
echo "   Initialization Complete!"
echo "=========================================="
echo ""
echo "  Frontend: http://localhost:5173"
echo "  Network:  http://${IP_ADDR}:5173"
echo "  Backend:  http://localhost:5000"
echo ""
echo "  Backend PID: $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""
echo "  Logs:"
echo "    - Backend: $SCRIPT_DIR/backend.log"
echo "    - Frontend: $SCRIPT_DIR/frontend.log"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "=========================================="

# Keep script running and handle cleanup
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
