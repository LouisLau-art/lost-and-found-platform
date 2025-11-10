#!/usr/bin/env bash

###############################################################################
# start-dev.sh                                                                #
#                                                                             #
# Cross-platform, cross-shell developer bootstrap for the Lost & Found app.  #
# Runs flawlessly when invoked from bash or fish thanks to this bash shebang. #
#                                                                             #
# Responsibilities                                                            #
#   * Verify core tooling (python3, node, npm)                                #
#   * Provision / reuse backend virtualenv and pip dependencies               #
#   * Provision / reuse frontend node_modules                                 #
#   * Launch backend (FastAPI + Uvicorn) & frontend (Vite) dev servers        #
#   * Cleanly tear everything down on Ctrl+C                                  #
###############################################################################

set -euo pipefail
# Make nvm available to this script
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

if [ -z "${BASH_VERSION:-}" ]; then
  echo "[WARN] start-dev.sh should be executed with bash. Falling back to POSIX sh." >&2
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend/frontend"

BACKEND_PID=""
FRONTEND_PID=""
VENV_BIN=""
CLEANED_UP=0

log_info() { printf '[INFO] %s\n' "$1"; }
log_success() { printf '[ OK ] %s\n' "$1"; }
log_warn() { printf '[WARN] %s\n' "$1"; }
log_error() { printf '[ERR ] %s\n' "$1" >&2; }

abort() {
  log_error "$1"
  exit 1
}

detect_os() {
  local uname_out
  uname_out="$(uname -s 2>/dev/null || echo Unknown)"
  case "$uname_out" in
    Linux*)
      if [ -f /proc/sys/kernel/osrelease ] && grep -qi 'microsoft' /proc/sys/kernel/osrelease; then
        OS_NAME="WSL"
        IS_WSL=true
      else
        OS_NAME="Linux"
        IS_WSL=false
      fi
      ;;
    Darwin*)
      OS_NAME="macOS"
      IS_WSL=false
      ;;
    CYGWIN*|MINGW*|MSYS*)
      OS_NAME="Windows"
      IS_WSL=false
      ;;
    *)
      OS_NAME="$uname_out"
      IS_WSL=false
      ;;
  esac
}

check_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    abort "Dependency '$cmd' is not available. Please install it and re-run this script."
  fi
}

# shellcheck disable=SC1090
activate_backend_venv() {
  if [ -f "$BACKEND_DIR/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$BACKEND_DIR/.venv/bin/activate"
    VENV_BIN="$BACKEND_DIR/.venv/bin"
  elif [ -f "$BACKEND_DIR/.venv/Scripts/activate" ]; then
    # shellcheck disable=SC1091
    source "$BACKEND_DIR/.venv/Scripts/activate"
    VENV_BIN="$BACKEND_DIR/.venv/Scripts"
  else
    abort "Virtual environment activation script not found in $BACKEND_DIR/.venv."
  fi
}

ensure_backend() {
  log_info "Setting up backend environment..."
  if [ ! -d "$BACKEND_DIR/.venv" ]; then
    log_info "Creating new virtual environment at backend/.venv"
    python3 -m venv "$BACKEND_DIR/.venv"
  else
    log_info "Using existing virtual environment at backend/.venv"
  fi

  activate_backend_venv

  if ! command -v uvicorn >/dev/null 2>&1; then
    log_info "Installing backend dependencies from requirements-sqlite.txt"
    pip install --upgrade pip >/dev/null 2>&1 || true
    pip install -r "$BACKEND_DIR/requirements-sqlite.txt"
  else
    log_info "Backend dependencies already present"
  fi
}

deactivate_backend() {
  if declare -f deactivate >/dev/null 2>&1; then
    deactivate
  fi
}

start_backend() {
  log_info "Starting backend server (FastAPI + Uvicorn)..."
  cd "$BACKEND_DIR"
  python -m uvicorn app.main:app --reload &
  BACKEND_PID=$!
  cd "$ROOT_DIR"
  log_success "Backend server PID $BACKEND_PID (http://127.0.0.1:8000)"
}

ensure_frontend() {
  log_info "Setting up frontend environment..."
  cd "$FRONTEND_DIR"
  if [ ! -d "node_modules" ]; then
    log_info "Installing frontend dependencies with npm install"
    npm install
  else
    log_info "Re-using existing node_modules"
  fi
  cd "$ROOT_DIR"
}

start_frontend() {
  log_info "Starting frontend dev server (Vite)..."
  cd "$FRONTEND_DIR"
  npm run dev -- --host 0.0.0.0 &
  FRONTEND_PID=$!
  cd "$ROOT_DIR"
  local url="http://localhost:5173"
  if [ "$IS_WSL" = true ]; then
    url="http://127.0.0.1:5173"
  fi
  log_success "Frontend server PID $FRONTEND_PID ($url)"
}

cleanup() {
  # Prevent running cleanup multiple times
  if [ "$CLEANED_UP" -eq 1 ]; then
    return
  fi
  CLEANED_UP=1

  log_info "Stopping services..."

  if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    log_info "Shutting down frontend (PID $FRONTEND_PID)"
    kill "$FRONTEND_PID" 2>/dev/null || true
    wait "$FRONTEND_PID" 2>/dev/null || true
  fi

  if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    log_info "Shutting down backend (PID $BACKEND_PID)"
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi

  deactivate_backend || true
  log_success "All services stopped."
}

trap 'cleanup; exit 0' INT TERM
trap 'cleanup' EXIT

detect_os
log_info "Detected platform: ${OS_NAME} (shell: ${SHELL:-unknown})"

check_command python3
check_command node
check_command npm

ensure_backend
start_backend
deactivate_backend || true

ensure_frontend
start_frontend

log_info "Both servers are running."
log_info "Backend:    http://127.0.0.1:8000"
log_info "Frontend:   http://localhost:5173"
log_warn "Press Ctrl+C to stop all services."

while true; do
  sleep 1
done
