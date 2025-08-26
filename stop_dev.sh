#!/bin/bash

# DataCharted Development Server Stop Script
echo "🛑 Stopping DataCharted Development Server..."

# Check if PID file exists
if [ -f "dev_server.pid" ]; then
    DEV_PID=$(cat dev_server.pid)
    
    # Check if process is still running
    if ps -p $DEV_PID > /dev/null; then
        echo "🔄 Stopping process $DEV_PID..."
        kill $DEV_PID
        
        # Wait a moment and check if it's stopped
        sleep 2
        if ps -p $DEV_PID > /dev/null; then
            echo "⚠️  Process still running, force stopping..."
            kill -9 $DEV_PID
        fi
        
        echo "✅ Development server stopped successfully!"
    else
        echo "ℹ️  Process $DEV_PID is not running"
    fi
    
    # Remove PID file
    rm dev_server.pid
else
    echo "ℹ️  No PID file found. Checking for Flask processes..."
    
    # Look for any Flask processes
    FLASK_PIDS=$(ps aux | grep "flask run" | grep -v grep | awk '{print $2}')
    
    if [ -n "$FLASK_PIDS" ]; then
        echo "🔄 Found Flask processes: $FLASK_PIDS"
        echo "🔄 Stopping all Flask processes..."
        echo $FLASK_PIDS | xargs kill
        echo "✅ All Flask processes stopped!"
    else
        echo "ℹ️  No Flask development servers found running"
    fi
fi

echo "🧹 Cleaning up log files..."
rm -f dev_server.log
echo "✅ Cleanup complete!"
