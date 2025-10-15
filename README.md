# AI-Powered Authentication Component Detector

A web application that automatically detects and analyzes authentication components on websites using **undetected-chromedriver** and AI-powered analysis with Ollama (Llama 3.2).

## 🎯 What This Application Does

This tool helps identify login forms and authentication mechanisms on any website by:

1. **Opening the website in a real Chrome browser** (visible, not headless)
2. **Extracting fully-rendered HTML** after all JavaScript has executed
3. **Detecting authentication components** using 9 different detection methods
4. **Analyzing results with AI** to provide insights about the authentication mechanism

### Why undetected-chromedriver?

- **🛡️ Bypasses bot detection** - Purpose-built to avoid anti-bot systems
- **👁️ Visual debugging** - See exactly what the browser sees
- **🚀 No complex setup** - Uses your system's Chrome installation
- **🔄 Auto-updates** - Automatically matches ChromeDriver to your Chrome version

---

## 📋 Prerequisites

Before setting up the project, ensure you have:

### 1. Python 3.8 or higher

```bash
python3 --version
```

### 2. Node.js and npm

```bash
node --version
npm --version
```

### 3. Google Chrome

- **macOS:** `brew install --cask google-chrome`
- **Ubuntu/Debian:** `sudo apt-get install google-chrome-stable`
- **Windows:** Download from [google.com/chrome](https://www.google.com/chrome/)

### 4. Ollama (for AI analysis)

```bash
# macOS
brew install ollama
brew services start ollama
ollama pull llama3.2

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2

# Windows
# Download from https://ollama.ai/download
```

---

## 🚀 Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd auth-detector-webapp-headful
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python test_chromedriver.py
```

**What happens during test:**

- Chrome will open visibly (this is normal!)
- Browser navigates to Instagram
- HTML is extracted after 5 seconds
- Browser closes automatically
- Results are displayed

### Step 3: Frontend Setup

```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Step 4: Start the Backend Server

```bash
# In the backend terminal (with venv activated)
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

---

## 🎮 How to Use

1. **Open the frontend** in your browser: `http://localhost:5173`

2. **Enter a URL** you want to analyze (e.g., `https://github.com/login`)

3. **Click "Analyze"**

4. **Watch the magic happen:**

   - Chrome browser will open visibly
   - Page loads with all JavaScript rendered
   - After 5 seconds, HTML is extracted
   - Browser closes automatically
   - Results appear on the screen

5. **View the results:**
   - Number of authentication components found
   - HTML snippets of login forms
   - AI analysis explaining the authentication method

---

## 🔧 How It Works

### Architecture Flow

```
User Input (URL)
    ↓
Frontend (React) → POST /analyze
    ↓
FastAPI Backend
    ↓
AuthDetector.detect_auth_components()
    ↓
undetected-chromedriver
    ├─ Launch Chrome (visible browser)
    ├─ Navigate to URL
    ├─ Wait for JavaScript (5 seconds)
    ├─ Extract page_source (fully rendered HTML)
    └─ Close browser
    ↓
BeautifulSoup HTML Parsing
    ├─ Method 1: Traditional forms with password inputs
    ├─ Method 2: Forms with login/signin classes
    ├─ Method 3: Instagram-style (username + password inputs)
    ├─ Method 4: WordPress-style (usernameOrEmail field)
    ├─ Method 5: ARIA-labeled password fields
    ├─ Method 6: Input combination detection
    ├─ Method 7: JavaScript/React containers
    ├─ Method 8: Data attributes (data-testid)
    └─ Method 9: Button context (login buttons near inputs)
    ↓
AI Analysis (Ollama/Llama 3.2)
    ├─ Analyzes detected components
    ├─ Identifies authentication method
    └─ Provides insights
    ↓
Return Results to Frontend
```

### Key Components

#### Backend (`backend/`)

- **`scraper.py`** - Core detection logic using undetected-chromedriver
- **`main.py`** - FastAPI server with /analyze endpoint
- **`agent.py`** - Optional agentic detection (enhanced mode)
- **`requirements.txt`** - Python dependencies

#### Frontend (`frontend/`)

- **`src/App.jsx`** - Main application component
- **`src/components/SingleUrlAnalyzer.jsx`** - URL input and analysis UI
- **`src/components/ResultCard.jsx`** - Display detected components
- **`src/services/api.js`** - API communication

---

## 📦 Dependencies

### Backend

- **undetected-chromedriver** - Anti-detection ChromeDriver
- **selenium** - Browser automation
- **beautifulsoup4** - HTML parsing
- **fastapi** - Web framework
- **ollama** - AI model integration

### Frontend

- **React** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling

---

## ⚙️ Configuration

### Change Wait Time

Edit `backend/scraper.py`, line ~176:

```python
time.sleep(5)  # Change to 10 for slower-loading pages
```

### Enable Headless Mode

Edit `backend/scraper.py`, line ~166, uncomment:

```python
options.add_argument('--headless=new')
```

### Keep Browser Open (for debugging)

Edit `backend/scraper.py`, line ~202, comment out:

```python
# driver.quit()
```

---

## 🧪 Testing

### Test Backend Only

```bash
cd backend
source venv/bin/activate
python test_chromedriver.py
```

### Test via API

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/login", "use_agents": false}'
```

### Test Full Stack

1. Start backend: `uvicorn main:app --reload`
2. Start frontend: `npm run dev`
3. Open `http://localhost:5173`
4. Enter a URL and click "Analyze"

---

## 🐛 Troubleshooting

### Chrome not found

```bash
# macOS
brew install --cask google-chrome

# Ubuntu
sudo apt-get install google-chrome-stable
```

### Module not found errors

```bash
pip install setuptools
pip install undetected-chromedriver selenium
```

### Port already in use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn main:app --reload --port 8001
```

### Ollama not running

```bash
# macOS
brew services start ollama

# Linux
ollama serve
```

---

## 📊 Detection Methods

The application uses **9 detection methods** for maximum accuracy:

1. **Traditional HTML Forms** - Standard `<form>` with password inputs
2. **Login Class Detection** - Forms with login/signin/auth classes
3. **Instagram-Style** - `name="username"` and `name="password"` inputs
4. **WordPress-Style** - `usernameOrEmail` or `user_login` fields
5. **ARIA Labels** - Password fields with `aria-label="password"`
6. **Input Combinations** - Username/email + password pairs
7. **JavaScript Containers** - React/Vue containers with auth classes
8. **Data Attributes** - Elements with `data-testid` containing auth keywords
9. **Button Context** - Login buttons near input fields

---

## 🔒 Bot Protection Detection

The application can detect if a site uses anti-bot protection:

- **DataDome**
- **PerimeterX**
- **Cloudflare Challenge**
- **reCAPTCHA**
- **hCaptcha**

If detected, the application will inform you that the site cannot be scraped programmatically.

---

## 📝 Example Results

### Successful Detection

```json
{
  "url": "https://github.com/login",
  "found": true,
  "components": [
    {
      "type": "html_login_form",
      "html": "<form>...</form>",
      "method": "traditional_html"
    }
  ],
  "ai_analysis": "This is a traditional username/password login form...",
  "method": "chromedriver",
  "captcha_detected": false
}
```

### Bot Protection Detected

```json
{
  "url": "https://medium.com/m/signin",
  "found": false,
  "components": [],
  "captcha_detected": true,
  "ai_analysis": "Site protected by anti-bot service..."
}
```

---

## 🚦 Project Structure

```
auth-detector-webapp-headful/
├── backend/
│   ├── agent.py              # Agentic detection (optional)
│   ├── main.py               # FastAPI server
│   ├── scraper.py            # Core detection logic
│   ├── requirements.txt      # Python dependencies
│   ├── test_chromedriver.py  # Test script
│   └── venv/                 # Virtual environment
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main app
│   │   ├── components/       # React components
│   │   └── services/         # API service
│   ├── package.json          # npm dependencies
│   └── vite.config.js        # Vite config
└── README.md                 # This file
```

---

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

## 📄 License

This project is for educational purposes.

---

## 🙏 Acknowledgments

- **undetected-chromedriver** by ultrafunkamsterdam
- **Ollama** for local AI inference
- **FastAPI** for the backend framework
- **React** and **Vite** for the frontend
