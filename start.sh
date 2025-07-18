#!/bin/bash

# Railway deployment startup script for Law AI Advisor Streamlit app
# Handles PORT environment variable properly

# Set default port if PORT is not set
PORT=${PORT:-8501}

echo "🚀 Starting Law AI Advisor on port $PORT"

# Run Streamlit with the correct port
exec streamlit run streamlit_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false