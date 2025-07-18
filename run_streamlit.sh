#!/bin/bash

# Law AI Advisor - Streamlit Launch Script
# Quick script to run the Streamlit chatbot locally

echo "🚀 Starting Law AI Advisor Streamlit Chatbot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements_streamlit.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before continuing."
    exit 1
fi

# Check if API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "❌ Please set your OPENAI_API_KEY in the .env file"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -q streamlit python-dotenv

# Run Streamlit app
echo "🌟 Launching Streamlit app..."
echo "📱 Open your browser to: http://localhost:8501"
echo "⏹️ Press Ctrl+C to stop"
echo ""

streamlit run streamlit_app.py