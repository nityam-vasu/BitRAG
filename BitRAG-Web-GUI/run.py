#!/usr/bin/env python3
"""
BitRAG Web GUI - Unified Run Script
Runs both backend and frontend servers from a single command.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path


# ANSI color codes
class Colors:
    INFO = "\033[94m"
    SUCCESS = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_info(msg):
    print(f"{Colors.INFO}[INFO]{Colors.ENDC} {msg}")


def print_success(msg):
    print(f"{Colors.SUCCESS}[SUCCESS]{Colors.ENDC} {msg}")


def print_warning(msg):
    print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}")


def print_error(msg):
    print(f"{Colors.ERROR}[ERROR]{Colors.ENDC} {msg}")


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent


def check_prerequisites():
    """Check if all prerequisites are installed."""
    print_info("Checking prerequisites...")

    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print_success(f"Python found: {result.stdout.strip()}")
    except Exception as e:
        print_error(f"Python not found: {e}")
        return False

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print_success(f"Node.js found: {result.stdout.strip()}")
    except Exception as e:
        print_error(f"Node.js not found: {e}")
        return False

    # Check Ollama (optional)
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        print_success("Ollama found")
    except Exception:
        print_warning("Ollama not found. Please install it from https://ollama.ai/download")

    return True


def run_script(script_name, command):
    """Run a sub-script with the given command."""
    project_root = get_project_root()
    script_path = project_root / script_name

    if not script_path.exists():
        print_error(f"Script not found: {script_name}")
        return False

    result = subprocess.run([sys.executable, str(script_path), command], check=False)
    return result.returncode == 0


def run_both(project_root):
    """Run both backend and frontend servers."""
    print_info("Starting both backend and frontend servers...")

    # Build frontend first
    if not run_script("run_frontend.py", "build"):
        return False

    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend"

    # Use venv python if it exists
    venv_python = (
        backend_dir / "venv" / "bin" / "python"
        if sys.platform != "win32"
        else backend_dir / "venv" / "Scripts" / "python.exe"
    )
    if venv_python.exists():
        python_cmd = str(venv_python)
    else:
        python_cmd = sys.executable

    # Start backend server in a separate thread
    def run_backend_server():
        subprocess.run([python_cmd, str(backend_dir / "app.py")])

    backend_thread = threading.Thread(target=run_backend_server, daemon=True)
    backend_thread.start()

    # Wait a moment for backend to start
    time.sleep(2)

    # Start frontend dev server in a separate thread
    def run_frontend_server():
        subprocess.run(["npm", "run", "dev"], cwd=str(frontend_dir))

    frontend_thread = threading.Thread(target=run_frontend_server, daemon=True)
    frontend_thread.start()

    print_success("Servers started!")
    print_info("Backend: http://localhost:5000")
    print_info("Frontend: http://localhost:5173")
    print_info("Press CTRL+C to stop all servers")

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_info("\nStopping servers...")
        return True


def show_usage():
    """Show usage information."""
    usage = """
BitRAG Web GUI - Unified Run Script

Usage: python run.py [command]

Commands:
  backend         - Start only the backend server
  frontend        - Start only the frontend dev server
  both            - Start both backend and frontend servers
  build           - Build frontend only
  install         - Install dependencies only
  help            - Show this help message

Examples:
  python run.py both         # Start both servers (recommended for development)
  python run.py backend      # Start backend only (serves built frontend)
  python run.py frontend     # Start frontend dev server only
"""
    print(usage)


def main():
    """Main entry point."""
    project_root = get_project_root()

    if len(sys.argv) < 2:
        print_info("No command specified, starting both servers...")
        if not check_prerequisites():
            return 1
        if not run_script("run_backend.py", "install"):
            return 1
        if not run_both(project_root):
            return 1
        return 0

    command = sys.argv[1].lower()

    if command == "backend":
        if not check_prerequisites():
            return 1
        if not run_script("run_backend.py", "install"):
            return 1
        if not run_script("run_frontend.py", "build"):
            return 1
        if not run_script("run_backend.py", "run"):
            return 1
    elif command == "frontend":
        if not check_prerequisites():
            return 1
        if not run_script("run_frontend.py", "run"):
            return 1
    elif command == "both":
        if not check_prerequisites():
            return 1
        if not run_script("run_backend.py", "install"):
            return 1
        if not run_both(project_root):
            return 1
    elif command == "build":
        if not check_prerequisites():
            return 1
        if not run_script("run_frontend.py", "build"):
            return 1
    elif command == "install":
        if not check_prerequisites():
            return 1
        if not run_script("run_backend.py", "install"):
            return 1
        if not run_script("run_frontend.py", "install"):
            return 1
    elif command in ("help", "--help", "-h"):
        show_usage()
    else:
        print_error(f"Unknown command: {command}")
        show_usage()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
