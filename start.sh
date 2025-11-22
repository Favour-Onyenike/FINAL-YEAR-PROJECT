#!/bin/bash

# Start the backend API server
echo "Starting FastAPI backend on port 8000..."
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

# Start the frontend server
echo "Starting frontend server on port 5000..."
python3 server.py
