#!/bin/bash

# Weavens Project Run Script
# This script helps start the development servers for the Weavens project.

set -e  # Exit immediately if a command exits with a non-zero status

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

# Root directory of the project
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Function to print section header
print_section() {
    echo -e "${BOLD}${GREEN}[RUN] $1${RESET}"
    echo "------------------------------------------------"
}

# Function to print error and exit
print_error() {
    echo -e "${BOLD}${RED}[ERROR] $1${RESET}"
    exit 1
}

# Function to print success message
print_success() {
    echo -e "${BOLD}${GREEN}[SUCCESS] $1${RESET}"
}

# Start backend server
start_backend() {
    print_section "Starting backend server"
    cd "$ROOT_DIR/backend"
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_error "Backend .env file not found. Please run setup.sh first."
    fi
    
    # Check if uv is installed
    if ! command -v uv &> /dev/null; then
        print_error "uv is required but not installed. Please install it and try again."
    fi
    
    echo "Starting backend server..."
    ENVIRONMENT=local uv run python -m src.main
}

# Start frontend server
start_frontend() {
    print_section "Starting frontend server"
    cd "$ROOT_DIR/frontend"
    
    # Check if .env.local file exists
    if [ ! -f ".env.local" ]; then
        print_error "Frontend .env.local file not found. Please run setup.sh first."
    fi
    
    # Check if node_modules directory exists
    if [ ! -d "node_modules" ]; then
        print_error "Frontend node_modules not found. Please run setup.sh first."
    fi
    
    echo "Starting frontend development server..."
    pnpm dev
}

# Show usage
show_usage() {
    echo -e "${BOLD}Usage:${RESET}"
    echo "  $0 [backend|frontend|all]"
    echo ""
    echo "  backend   Start only the backend server"
    echo "  frontend  Start only the frontend server"
    echo "  all       Start both backend and frontend servers (in separate terminals)"
    echo ""
}

# Main function
main() {
    if [ "$#" -eq 0 ]; then
        show_usage
        exit 1
    fi
    
    case "$1" in
        backend)
            start_backend
            ;;
        frontend)
            start_frontend
            ;;
        all)
            # Start backend and frontend in separate terminals
            # This may need adjustments based on the user's OS/terminal
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                open -a Terminal.app "$ROOT_DIR/scripts/run.sh backend"
                open -a Terminal.app "$ROOT_DIR/scripts/run.sh frontend"
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                # Linux with X11
                if command -v gnome-terminal &> /dev/null; then
                    gnome-terminal -- "$ROOT_DIR/scripts/run.sh" backend
                    gnome-terminal -- "$ROOT_DIR/scripts/run.sh" frontend
                elif command -v xterm &> /dev/null; then
                    xterm -e "$ROOT_DIR/scripts/run.sh backend" &
                    xterm -e "$ROOT_DIR/scripts/run.sh frontend" &
                else
                    print_error "Could not find a suitable terminal emulator. Please run backend and frontend manually."
                fi
            else
                print_error "Unsupported operating system. Please run backend and frontend manually."
            fi
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Execute main function with arguments
main "$@" 