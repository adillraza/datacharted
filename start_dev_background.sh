#!/bin/bash

# DataCharted Development Server Background Startup Script
echo "🚀 Starting DataCharted Development Server in background..."

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export FLASK_APP=run.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start Flask development server in background
nohup flask run --host=0.0.0.0 --port=5000 > dev_server.log 2>&1 &

# Get the process ID
DEV_PID=$!

# Save PID to file for easy stopping
echo $DEV_PID > dev_server.pid

echo "✅ Development server started successfully!"
echo "📍 Server is running at: http://localhost:5000"
echo "📍 Network access: http://192.168.18.176:5000"
echo "📝 Logs are saved to: dev_server.log"
echo "🆔 Process ID: $DEV_PID (saved to dev_server.pid)"
echo ""
echo "💡 To stop the server, run: ./stop_dev.sh"
echo "💡 To view logs, run: tail -f dev_server.log"
echo "💡 To check status, run: ps aux | grep flask"
