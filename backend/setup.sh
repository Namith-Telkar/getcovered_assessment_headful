#!/bin/bash

echo "🚀 Setting up Auth Detector Backend..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip3 install -r requirements.txt

# Install Playwright browsers
echo "🎭 Installing Playwright Chromium browser..."
python3 -m playwright install chromium

echo "✅ Setup complete!"
echo ""
echo "To start the server, run:"
echo "  uvicorn main:app --reload"
