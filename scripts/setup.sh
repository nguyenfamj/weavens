#!/bin/bash

# Weavens Project Setup Script
# This script helps set up the local development environment for the Weavens project.

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
    echo -e "${BOLD}${GREEN}[SETUP] $1${RESET}"
    echo "------------------------------------------------"
}

# Function to print error and exit
print_error() {
    echo -e "${BOLD}${RED}[ERROR] $1${RESET}"
    exit 1
}

# Function to print warning
print_warning() {
    echo -e "${BOLD}${YELLOW}[WARNING] $1${RESET}"
}

# Function to print success message
print_success() {
    echo -e "${BOLD}${GREEN}[SUCCESS] $1${RESET}"
}

# Function to check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is required but not installed. Please install it and try again."
    fi
}

# Function to compare version numbers
version_compare() {
    # $1 = version1, $2 = version2
    # Returns: 0 if version1 >= version2, 1 if version1 < version2
    if [[ "$1" == "$2" ]]; then
        return 0
    fi
    
    local IFS=.
    local i ver1=($1) ver2=($2)
    
    # Fill empty fields with zeros
    for ((i=0; i<${#ver2[@]}; i++)); do
        if [[ -z ${ver1[i]} ]]; then
            ver1[i]=0
        fi
    done
    
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 0
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 1
        fi
    done
    
    return 0
}

# Check prerequisites
check_prerequisites() {
    print_section "Checking prerequisites"
    
    check_command "docker"
    check_command "docker-compose"
    check_command "terraform"
    check_command "python3"
    check_command "uv"
    check_command "node"
    check_command "pnpm"
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if ! version_compare "$python_version" "3.10"; then
        print_error "Python 3.10 or higher is required. You have Python $python_version"
    fi
    
    # Check Node.js version
    node_version=$(node -v | cut -d "v" -f 2 | cut -d "." -f 1)
    if [ "$node_version" -lt 20 ]; then
        print_error "Node.js 20 or higher is required. You have Node.js $(node -v)"
    fi
    
    print_success "All prerequisites are installed!"
}

# Setup environment files
setup_env_files() {
    print_section "Setting up environment files"
    
    # Backend .env
    if [ ! -f "$ROOT_DIR/backend/.env" ]; then
        if [ -f "$ROOT_DIR/backend/.env.example" ]; then
            cp "$ROOT_DIR/backend/.env.example" "$ROOT_DIR/backend/.env"
            print_warning "Created backend/.env from example. You may need to update it with your specific settings."
        else
            print_error "backend/.env.example not found. Cannot create backend/.env"
        fi
    else
        print_success "backend/.env already exists."
    fi
    
    # Frontend .env
    if [ ! -f "$ROOT_DIR/frontend/.env.local" ]; then
        if [ -f "$ROOT_DIR/frontend/.env.example" ]; then
            cp "$ROOT_DIR/frontend/.env.example" "$ROOT_DIR/frontend/.env.local"
            print_warning "Created frontend/.env.local from example. You may need to update it with your specific settings."
        else
            print_error "frontend/.env.example not found. Cannot create frontend/.env.local"
        fi
    else
        print_success "frontend/.env.local already exists."
    fi
    
    # Docker .env
    if [ ! -f "$ROOT_DIR/docker/.env" ]; then
        if [ -f "$ROOT_DIR/docker/.env.example" ]; then
            cp "$ROOT_DIR/docker/.env.example" "$ROOT_DIR/docker/.env"
            print_warning "Created docker/.env from example. You may need to update it with your specific settings."
        else
            print_error "docker/.env.example not found. Cannot create docker/.env"
        fi
    else
        print_success "docker/.env already exists."
    fi
}

# Start Docker containers
start_docker() {
    print_section "Starting Docker containers"
    
    cd "$ROOT_DIR/docker"
    docker-compose up -d
    
    if [ $? -ne 0 ]; then
        print_error "Failed to start Docker containers. Please check the error messages above."
    fi
    
    print_success "Docker containers started successfully!"
}

# Apply Terraform configuration
apply_terraform() {
    print_section "Applying Terraform configuration"
    
    cd "$ROOT_DIR/infra/environments/local"
    
    # Run terraform init regardless if .terraform exists
    # This ensures module dependencies are always up to date
    echo "Running terraform init..."
    terraform init
    
    if [ $? -ne 0 ]; then
        print_error "Failed to initialize Terraform. Please check the error messages above."
    fi
    
    echo "Running terraform apply..."
    terraform apply -auto-approve || {
        if grep -q "ResourceInUseException" <<< "$(terraform apply -auto-approve 2>&1)"; then
            print_warning "Some DynamoDB tables already exist. This is not an error for local development."
        else
            print_error "Failed to apply Terraform configuration. Please check the error messages above."
        fi
    }
    
    print_success "Terraform configuration completed! (Some resources may already exist)"
}

# Setup backend
setup_backend() {
    print_section "Setting up backend"
    
    cd "$ROOT_DIR/backend"
    
    echo "Creating virtual environment for backend..."
    uv venv
    
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment. Please check the error messages above."
    fi
    
    echo "Installing backend dependencies with uv..."
    uv pip install -e .
    
    if [ $? -ne 0 ]; then
        print_error "Failed to install backend dependencies. Please check the error messages above."
    fi
    
    print_success "Backend dependencies installed successfully!"
}

# Setup frontend
setup_frontend() {
    print_section "Setting up frontend"
    
    cd "$ROOT_DIR/frontend"
    
    echo "Installing frontend dependencies with pnpm..."
    pnpm install
    
    if [ $? -ne 0 ]; then
        print_error "Failed to install frontend dependencies. Please check the error messages above."
    fi
    
    print_success "Frontend dependencies installed successfully!"
}

# Main function
main() {
    print_section "Starting Weavens setup process"
    
    check_prerequisites
    setup_env_files
    start_docker
    apply_terraform
    setup_backend
    setup_frontend
    
    print_success "Setup completed successfully!"
    echo ""
    echo -e "${BOLD}You can now start the development servers:${RESET}"
    echo ""
    echo -e "  Backend:   ${YELLOW}cd backend && ENVIRONMENT=local uv run python -m src.main${RESET}"
    echo -e "  Frontend:  ${YELLOW}cd frontend && pnpm dev${RESET}"
    echo ""
    echo -e "${BOLD}Happy coding!${RESET}"
}

# Execute main function
main 