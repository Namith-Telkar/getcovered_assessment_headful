# AI-Powered Authentication Component Detector

A web application that uses AI (Llama 3.2) to detect authentication components on websites.

## Features

- Web scraping with intelligent authentication detection
- AI-powered HTML analysis using local Llama model
- React frontend with real-time results
- Handles multi-step login flows
- **Dynamic JavaScript detection** - automatically detects if a page needs JS rendering
- **JavaScript rendering** for modern SPAs (Instagram, Twitter, WordPress, etc.)
- **9 detection methods** for maximum accuracy

## Setup

### Prerequisites

```bash
# Install Ollama (macOS)
brew install ollama
brew services start ollama
ollama pull llama3.2

# For Linux:
# curl -fsSL https://ollama.ai/install.sh | sh
# ollama pull llama3.2
```

### Backend

```bash
cd backend
pip install -r requirements.txt

# Install Playwright browsers (required for JavaScript-heavy sites like Instagram)
playwright install chromium
python -m playwright install chromium

uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Enter a website URL
2. Click "Analyze"
3. View detected authentication components
