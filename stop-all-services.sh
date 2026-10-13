#!/bin/bash
# AetherOps - Stop All Services

echo "Stopping all AetherOps services..."
pkill -f 'uvicorn app.main:app'
sleep 2
echo "✓ All services stopped"
