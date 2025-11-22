#!/bin/bash

# =============================================================================
# UNIMARKET STARTUP SCRIPT
# =============================================================================
# This script starts both the backend API and frontend web server.
# It runs them as background processes so both can run simultaneously.

# WHAT IT DOES:
# 1. Start FastAPI backend server on port 8000
# 2. Start Python HTTP server (frontend) on port 5000
# Both servers run in parallel

# HOW TO RUN:
# bash start.sh

# WHAT YOU'LL SEE:
# "Starting FastAPI backend on port 8000..."
# "Starting frontend server on port 5000..."

# TO STOP:
# Press Ctrl+C to stop both servers

# =============================================================================
# START BACKEND SERVER
# =============================================================================
# uvicorn = ASGI server that runs FastAPI
# backend.main:app = Run the FastAPI app from backend/main.py
# --host 127.0.0.1 = Listen on localhost only (for backend)
# --port 8000 = Listen on port 8000
# & = Run in background so we can start frontend too

echo "Starting FastAPI backend on port 8000..."
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

# =============================================================================
# START FRONTEND SERVER
# =============================================================================
# This starts server.py (Python's SimpleHTTPServer)
# This serves the static HTML/CSS/JavaScript files
# --host 0.0.0.0:5000 = Listen on all interfaces, port 5000
# No & here because it runs in foreground (frontend server is the "main" process)

echo "Starting frontend server on port 5000..."
python3 server.py

# Note: When you Ctrl+C, it stops the frontend server
# The backend server (running in background) will also stop
