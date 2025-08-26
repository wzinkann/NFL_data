#!/bin/bash

echo "🏈 Starting NFL Game Outcome Prediction API..."
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "📝 Please edit .env file and add your Tank01 API key"
        echo "   Then restart the API"
    else
        echo "❌ env.example not found. Please create .env file manually."
    fi
fi

# Start the API
echo "🚀 Starting API server..."
echo "   API will be available at: http://localhost:8000"
echo "   Documentation: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"
echo ""

python main.py
