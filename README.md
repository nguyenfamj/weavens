<p align="center"> 
  <h1 align="center">Weavens</h1>
</p>

<p align="center">
  <img src="https://img.shields.io/github/v/release/nguyenfamj/weavens?label=version">
  <img src="https://img.shields.io/badge/license-MIT-green">
</p>

Weavens is a platform for finding apartments in Finland.

# 🛠️ Local Development

You can set up a Weavens development environment by following the guide below for your operating system:

Prerequisites:

- Docker
- Python 3.10
- uv
- terraform
- Node.js 20
- pnpm

## 🚀 Quick Setup

We provide scripts to help you quickly set up and run the project:

### Automated Setup

Run the setup script to prepare your environment:

```bash
# Make scripts executable (if needed)
chmod +x scripts/setup.sh scripts/run.sh

# Run the setup script
./scripts/setup.sh
```

This script will:

1. Check prerequisites
2. Set up environment files
3. Start Docker containers
4. Apply Terraform configuration to create DynamoDB tables
5. Install backend dependencies with uv
6. Install frontend dependencies with pnpm

### Running the Project

After setup, you can use the run script to start development servers:

```bash
# Start backend server only
./scripts/run.sh backend

# Start frontend server only
./scripts/run.sh frontend

# Start both backend and frontend (in separate terminals)
./scripts/run.sh all
```

## 📦 Manual Setup

If you prefer to set up components manually, follow these steps:

### Backend

## 📦 Frontend

## 📦 Search
