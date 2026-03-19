#!/usr/bin/env python3
"""
BitRAG Web GUI - Backend Run Script
Handles backend dependencies and server execution.
"""

import os
import sys
import subprocess
from pathlib import Path


# ANSI color codes
class Colors:
    INFO = "\033[94m"
    SUCCESS = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    ENDC = "\033[0m"


def print_info(msg):
    print(f"{Colors.INFO}[INFO]{Colors.ENDC} {msg}")


def print_success(msg):
    print(f"{Colors.SUCCESS}[SUCCESS]{Colors.ENDC} {msg}")


def print_error(msg):
    print(f"{Colors.ERROR}[ERROR]{Colors.ENDC} {msg}")


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent


def check_prerequisites():
    """Check if Python is installed."""
    print_info("Checking Python...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print_success(f"Python found: {result.stdout.strip()}")
        return True
    except Exception as e:
        print_error(f"Python not found: {e}")
        return False


def install_backend_deps(project_root):
    """Install backend dependencies."""
    print_info("Installing backend dependencies...")
    backend_dir = project_root / "backend"

    if not (backend_dir / "requirements.txt").exists():
        print_error("requirements.txt not found in backend directory")
        return False

    # Check if venv exists, if not create it
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print_info("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    # Install dependencies
    pip_path = (
        venv_dir / "bin" / "pip" if sys.platform != "win32" else venv_dir / "Scripts" / "pip.exe"
    )
    if not pip_path.exists():
        print_error(f"pip not found at {pip_path}")
        return False

    subprocess.run(
        [str(pip_path), "install", "-r", str(backend_dir / "requirements.txt")], check=True
    )
    print_success("Backend dependencies installed")
    return True


def run_backend(project_root):
    """Run the backend server."""
    print_info("Starting backend server...")
    backend_dir = project_root / "backend"

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

    print_success("Backend server running at http://localhost:5000")
    subprocess.run([python_cmd, str(backend_dir / "app.py")], check=True)


def show_usage():
    """Show usage information."""
    usage = """
BitRAG Web GUI - Backend Run Script

Usage: python run_backend.py [command]

Commands:
  install         - Install backend dependencies only
  run             - Run the backend server (requires dependencies installed)
  help            - Show this help message

Examples:
  python run_backend.py install  # Install dependencies
  python run_backend.py run      # Run backend server
"""
    print(usage)


def main():
    """Main entry point."""
    project_root = get_project_root()

    if len(sys.argv) < 2:
        print_error("No command specified.")
        show_usage()
        return 1

    command = sys.argv[1].lower()

    if command == "install":
        if not check_prerequisites():
            return 1
        if not install_backend_deps(project_root):
            return 1
    elif command == "run":
        if not run_backend(project_root):
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
