#!/bin/bash

# DataCharted Development Server Startup Script
echo "🚀 Starting DataCharted Development Server..."

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export FLASK_APP=run.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start Flask development server
echo "📍 Server will be available at: http://localhost:5000"
echo "📍 Network access: http://192.168.18.176:5000"
echo "🔧 Debug mode: ON"
echo "📱 Press Ctrl+C to stop the server"
echo ""

# Start the server
flask run --host=0.0.0.0 --port=5000
