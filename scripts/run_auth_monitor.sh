#!/bin/bash

# Amazon SP API Authentication Monitor Runner
# This script activates the virtual environment and runs the authentication monitor

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔐 Amazon SP API Authentication Monitor"
echo "========================================"
echo "Project root: $PROJECT_ROOT"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "❌ Virtual environment not found at $PROJECT_ROOT/venv"
    echo "Please create the virtual environment first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$PROJECT_ROOT/venv/bin/activate"

# Check if we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"
echo ""

# Change to project directory
cd "$PROJECT_ROOT"

# Check if required packages are installed
echo "🔍 Checking required packages..."
if ! python -c "import sp_api" 2>/dev/null; then
    echo "❌ python-amazon-sp-api package not found"
    echo "Please install it: pip install python-amazon-sp-api"
    exit 1
fi

if ! python -c "import django" 2>/dev/null; then
    echo "❌ Django package not found"
    echo "Please install requirements: pip install -r requirements.txt"
    exit 1
fi

echo "✅ All required packages are installed"
echo ""

# Run the authentication monitor
echo "🚀 Starting Amazon SP API Authentication Monitor..."
echo "This will run for 90 minutes (1.5 hours) with tests every minute"
echo "Press Ctrl+C to stop early"
echo ""

python scripts/amazon_auth_monitor.py

echo ""
echo "✅ Authentication monitor completed" 