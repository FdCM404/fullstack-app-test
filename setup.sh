#!/usr/bin/env bash

# Setup Script

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[SKIP]${NC}  $*"; }
fail()  { echo -e "${RED}[ERR]${NC}   $*"; exit 1; }

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

info "Checking required system tools..."

for cmd in python3 pip3 node npm; do
    if ! command -v "$cmd" &>/dev/null; then
        fail "'$cmd' is not installed. Please install it before running this script."
    fi
done

info "python3 : $(python3 --version)"
info "pip3    : $(pip3 --version | head -c 40)..."
info "node    : $(node --version)"
info "npm     : $(npm --version)"
echo


# 1. Backend – Python virtual-env, dependencies

VENV_DIR="$ROOT_DIR/backend-venv"
PIP="$VENV_DIR/bin/pip"
PYTHON="$VENV_DIR/bin/python"

BACKEND_PACKAGES=(flask flask-sqlalchemy flask-cors)

# 1a. Create venv if missing
if [ -f "$PYTHON" ]; then
    warn "Python venv already exists at $VENV_DIR"
else
    info "Creating Python virtual environment at $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
    info "Virtual environment created."
fi

# 1b. Install each pip package only if not already present
info "Checking backend Python packages..."
for pkg in "${BACKEND_PACKAGES[@]}"; do
    if "$PIP" show "$pkg" &>/dev/null; then
        warn "pip package '$pkg' is already installed."
    else
        info "Installing pip package '$pkg' ..."
        "$PIP" install "$pkg"
    fi
done
echo

# 2. Frontend – Vite / React scaffold & npm dependencies

FRONTEND_DIR="$ROOT_DIR/frontend"

# 3. Scaffold only if the frontend directory does NOT exist
if [ -d "$FRONTEND_DIR" ]; then
    warn "frontend/ directory already exists – skipping Vite scaffold."
else
    info "Scaffolding React frontend with Vite ..."
    cd "$ROOT_DIR"
    npm create vite@latest frontend -- --template react
fi

# 3a. Install npm packages if node_modules is missing or empty
cd "$FRONTEND_DIR"

if [ -d "node_modules" ] && [ "$(ls -A node_modules 2>/dev/null)" ]; then
    warn "node_modules/ already populated – skipping 'npm install'."
else
    info "Installing frontend npm dependencies ..."
    npm install
fi

# 3b. Install react-router-dom if not already present
if [ -d "node_modules/react-router-dom" ]; then
    warn "react-router-dom is already installed."
else
    info "Installing react-router-dom ..."
    npm install react-router-dom
fi

# Also make sure root-level react-router-dom is installed (root package.json)
cd "$ROOT_DIR"
if [ -d "node_modules/react-router-dom" ]; then
    warn "Root-level react-router-dom is already installed."
else
    info "Installing root-level react-router-dom ..."
    npm install react-router-dom
fi
echo


# 4. Initialise the database & create admin user

info "Initialising database & creating admin user ..."
cd "$ROOT_DIR"
"$PYTHON" adminCreate.py
echo


# 5. Done – print quick-start instructions

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Setup complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo
echo "  Start the backend:"
echo "    cd backend && ../backend-venv/bin/python main.py"
echo
echo "  Start the frontend (in another terminal):"
echo "    cd frontend && npm run dev"
echo
