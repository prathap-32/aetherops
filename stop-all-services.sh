#!/bin/bash
# AetherOps - Stop All Services

echo "Stopping all AetherOps services..."
pkill -f 'uvicorn.*app.main:app' 2>/dev/null || true
pkill -f 'uvicorn.*main:app' 2>/dev/null || true
pkill -f 'uvicorn app.main:app' 2>/dev/null || true
sleep 1
echo "✓ All services stopped"
