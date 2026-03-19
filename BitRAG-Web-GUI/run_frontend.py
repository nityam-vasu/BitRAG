#!/usr/bin/env python3
"""
BitRAG Web GUI - Frontend Run Script
Handles frontend building and dev server execution.
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
    """Check if Node.js is installed."""
    print_info("Checking Node.js...")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print_success(f"Node.js found: {result.stdout.strip()}")
        return True
    except Exception as e:
        print_error(f"Node.js not found: {e}")
        return False


def install_frontend_deps(project_root):
    """Install frontend dependencies."""
    print_info("Installing frontend dependencies...")
    frontend_dir = project_root / "frontend"

    if not (frontend_dir / "package.json").exists():
        print_error("package.json not found in frontend directory")
        return False

    subprocess.run(["npm", "install"], cwd=str(frontend_dir), check=True)
    print_success("Frontend dependencies installed")
    return True


def build_frontend(project_root):
    """Build the frontend."""
    print_info("Building frontend...")
    frontend_dir = project_root / "frontend"

    if not (frontend_dir / "package.json").exists():
        print_error("package.json not found in frontend directory")
        return False

    # Install dependencies if node_modules doesn't exist
    if not (frontend_dir / "node_modules").exists():
        print_info("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=str(frontend_dir), check=True)

    # Build frontend
    subprocess.run(["npm", "run", "build"], cwd=str(frontend_dir), check=True)

    # Copy built files to backend static directory
    print_info("Copying built frontend to backend/static...")
    static_dir = project_root / "backend" / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    # Remove existing static files
    for item in static_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            import shutil

            shutil.rmtree(item)

    # Copy new files
    dist_dir = frontend_dir / "dist"
    if dist_dir.exists():
        import shutil

        for item in dist_dir.iterdir():
            dest = static_dir / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)

    print_success("Frontend built and copied to backend/static/")
    return True


def run_frontend_dev(project_root):
    """Run the frontend dev server."""
    print_info("Starting frontend dev server...")
    frontend_dir = project_root / "frontend"

    print_success("Frontend dev server running at http://localhost:5173")
    subprocess.run(["npm", "run", "dev"], cwd=str(frontend_dir), check=True)


def show_usage():
    """Show usage information."""
    usage = """
BitRAG Web GUI - Frontend Run Script

Usage: python run_frontend.py [command]

Commands:
  install         - Install frontend dependencies only
  build           - Build frontend only
  run             - Run frontend dev server only
  help            - Show this help message

Examples:
  python run_frontend.py install  # Install dependencies
  python run_frontend.py build    # Build frontend
  python run_frontend.py run      # Run dev server
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
        if not install_frontend_deps(project_root):
            return 1
    elif command == "build":
        if not check_prerequisites():
            return 1
        if not build_frontend(project_root):
            return 1
    elif command == "run":
        if not check_prerequisites():
            return 1
        if not run_frontend_dev(project_root):
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
