#!/bin/bash

# BitRAG Web GUI - Run Server Script
# This script starts both backend and frontend servers

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    print_success "Node.js found: $(node --version)"
    
    # Check Ollama
    if ! command -v ollama &> /dev/null; then
        print_warning "Ollama is not installed. Please install it from https://ollama.ai/download"
    else
        print_success "Ollama found"
        # Check if Ollama is running
        if ! curl -s http://localhost:11434/api/tags > /dev/null; then
            print_warning "Ollama is not running. Please start it with 'ollama serve' or run the Ollama app"
        fi
    fi
}

# Run sub-script
run_script() {
    local script_name=$1
    local command=$2
    
    if [ ! -f "$PROJECT_ROOT/$script_name" ]; then
        print_error "Script not found: $script_name"
        return 1
    fi
    
    python3 "$PROJECT_ROOT/$script_name" "$command"
    return $?
}

# Run both servers
run_both() {
    print_info "Starting both backend and frontend servers..."
    
    # Kill any existing processes on ports 5000 and 5173
    print_info "Checking for existing processes on ports 5000 and 5173..."
    
    # Check port 5000
    if lsof -ti:5000 > /dev/null; then
        print_warning "Process found on port 5000, killing it..."
        kill -9 $(lsof -ti:5000) 2>/dev/null || true
    fi
    
    # Check port 5173
    if lsof -ti:5173 > /dev/null; then
        print_warning "Process found on port 5173, killing it..."
        kill -9 $(lsof -ti:5173) 2>/dev/null || true
    fi
    
    # Build frontend first
    build_frontend
    
    # Start backend in background
    cd "$PROJECT_ROOT/backend"
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    print_info "Starting backend server on port 5000..."
    python3 app.py &
    BACKEND_PID=$!
    
    # Wait a moment for backend to start
    sleep 2
    
    # Start frontend dev server
    cd "$PROJECT_ROOT/frontend"
    print_info "Starting frontend dev server on port 5173..."
    npm run dev &
    FRONTEND_PID=$!
    
    print_success "Servers started!"
    print_info "Backend: http://localhost:5000"
    print_info "Frontend: http://localhost:5173"
    print_info "Press CTRL+C to stop all servers"
    
    # Wait for user interrupt
    trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
    wait
}

# Show usage
show_usage() {
    echo "BitRAG Web GUI - Run Server Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  backend         - Start only the backend server"
    echo "  frontend        - Start only the frontend dev server"
    echo "  both            - Start both backend and frontend servers"
    echo "  build           - Build frontend only"
    echo "  install         - Install dependencies only"
    echo "  help            - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 both         # Start both servers (recommended for development)"
    echo "  $0 backend      # Start backend only (serves built frontend)"
    echo "  $0 frontend     # Start frontend dev server only"
    echo ""
}

# Main script logic
main() {
    case "${1:-}" in
        backend)
            check_prerequisites
            run_script "run_backend.py" "install"
            run_script "run_frontend.py" "build"
            run_script "run_backend.py" "run"
            ;;
        frontend)
            check_prerequisites
            run_script "run_frontend.py" "run"
            ;;
        both)
            check_prerequisites
            run_script "run_backend.py" "install"
            run_both
            ;;
        build)
            check_prerequisites
            run_script "run_frontend.py" "build"
            ;;
        install)
            check_prerequisites
            run_script "run_backend.py" "install"
            run_script "run_frontend.py" "install"
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_info "No command specified, starting both servers..."
            check_prerequisites
            run_script "run_backend.py" "install"
            run_both
            ;;
    esac
}

# Run main function with all arguments
main "$@"
