# System Architecture & Design Documentation

## 📐 Architecture Overview

This document provides a comprehensive overview of the AI-Powered Authentication Component Detector system architecture, including component interactions, data flow, and deployment architecture.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                         │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    React Frontend (Vite)                       │  │
│  │  • SingleUrlAnalyzer.jsx  - URL input & examples              │  │
│  │  • ResultCard.jsx         - Results display with markdown     │  │
│  │  • Header.jsx             - App branding                      │  │
│  │  • api.js                 - API client service                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              Port: 5173                              │
└──────────────────────────────┬──────────────────────────────────────┘
                                │ HTTP/REST API
                                │ POST /analyze
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                              │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                   FastAPI Backend Server                       │  │
│  │  • main.py        - API endpoints & orchestration             │  │
│  │  • CORS enabled   - Cross-origin requests                     │  │
│  │  • Pydantic       - Request/response validation               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              Port: 8000                              │
└──────────────────┬─────────────────────┬────────────────────────────┘
                   │                     │
                   ▼                     ▼
┌──────────────────────────────┐  ┌─────────────────────────────────┐
│   DETECTION ENGINE LAYER     │  │   AI ENHANCEMENT LAYER          │
│                              │  │                                 │
│  ┌────────────────────────┐ │  │  ┌───────────────────────────┐ │
│  │   scraper.py           │ │  │  │   agent.py                │ │
│  │  ┌──────────────────┐  │ │  │  │  ┌─────────────────────┐ │ │
│  │  │ ChromeDriver     │  │ │  │  │  │ Playwright          │ │ │
│  │  │ • Visible browser│  │ │  │  │  │ • Dynamic detection │ │ │
│  │  │ • Anti-bot bypass│  │ │  │  │  │ • Click simulation  │ │ │
│  │  │ • 5s page wait   │  │ │  │  │  │ • Navigation logic  │ │ │
│  │  └──────────────────┘  │ │  │  └─────────────────────────┘ │ │
│  │  ┌──────────────────┐  │ │  │  ┌───────────────────────┐   │ │
│  │  │ BeautifulSoup    │  │ │  │  │ AI Validation         │   │ │
│  │  │ • 9 detection    │  │ │  │  │ • Confidence scoring  │   │ │
│  │  │   methods        │  │ │  │  │ • Result enhancement  │   │ │
│  │  └──────────────────┘  │ │  │  └───────────────────────┘   │ │
│  └────────────────────────┘ │  └─────────────────────────────────┘
└──────────────────────────────┘                │
                   │                            │
                   └────────────┬───────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         AI ANALYSIS LAYER                            │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Ollama (Llama 3.2)                          │  │
│  │  • Local AI inference                                          │  │
│  │  • Context-aware analysis                                      │  │
│  │  • Markdown-formatted responses                                │  │
│  │  • Authentication method identification                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                            Port: 11434                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow Diagram

### Standard Detection Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │ 1. Enter URL
     │    (e.g., https://github.com/login)
     ▼
┌─────────────────────┐
│  React Frontend     │
│  SingleUrlAnalyzer  │
└────┬────────────────┘
     │ 2. POST /analyze
     │    { url: "...", use_agents: true }
     ▼
┌─────────────────────────────────────────────────────────┐
│             FastAPI Backend (main.py)                   │
│                                                          │
│  Step 3: Initialize AuthDetector                        │
│  Step 4: Call detect_auth_components(url)              │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│         Detection Engine (scraper.py)                   │
│                                                          │
│  Step 5: Launch undetected-chromedriver                │
│          ┌──────────────────────────────┐              │
│          │  Chrome Browser Opens        │              │
│          │  • Visible window            │              │
│          │  • Navigate to URL           │              │
│          │  • Wait 5 seconds            │              │
│          │  • Extract page_source       │              │
│          │  • Close browser             │              │
│          └──────────────────────────────┘              │
│                                                          │
│  Step 6: Parse HTML with BeautifulSoup                 │
│          Run 9 detection methods:                       │
│          ✓ Traditional forms                            │
│          ✓ Login class detection                        │
│          ✓ Instagram-style inputs                       │
│          ✓ WordPress-style fields                       │
│          ✓ ARIA labels                                  │
│          ✓ Input combinations                           │
│          ✓ JavaScript containers                        │
│          ✓ Data attributes                              │
│          ✓ Button context                               │
│                                                          │
│  Step 7: Check for bot protection                      │
│          • DataDome, PerimeterX                         │
│          • Cloudflare, reCAPTCHA                        │
│          • hCaptcha                                     │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│            AI Analysis (Ollama)                         │
│                                                          │
│  Step 8: If components found:                           │
│          • Send HTML + components to Llama 3.2          │
│          • Analyze authentication method                │
│          • Generate markdown insights                   │
│                                                          │
│  Step 9: If components not found:                       │
│          • Analyze why detection failed                 │
│          • Suggest alternatives                         │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│        AI Enhancement (agent.py) - Optional             │
│                                                          │
│  Step 10: If use_agents=true:                           │
│           • Validate static results with AI             │
│           • Or perform dynamic detection if failed      │
│                                                          │
│           Dynamic Detection Flow:                       │
│           ┌──────────────────────────────┐             │
│           │  Playwright Browser          │             │
│           │  • Click login buttons       │             │
│           │  • Navigate auth paths       │             │
│           │  • Extract dynamic forms     │             │
│           └──────────────────────────────┘             │
└────┬────────────────────────────────────────────────────┘
     │
     │ 11. Return JSON Response
     ▼
┌─────────────────────────────────────────────────────────┐
│             FastAPI Backend                             │
│  {                                                       │
│    "url": "https://github.com/login",                   │
│    "found": true,                                        │
│    "components": [...],                                  │
│    "ai_analysis": "# Analysis\n...",                    │
│    "captcha_detected": false                            │
│  }                                                       │
└────┬────────────────────────────────────────────────────┘
     │
     │ 12. Display Results
     ▼
┌─────────────────────────────────────────────────────────┐
│           React Frontend (ResultCard.jsx)               │
│                                                          │
│  • Parse markdown AI analysis (react-markdown)          │
│  • Display component details                            │
│  • Show formatted HTML snippets                         │
│  • Render CAPTCHA warnings if detected                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Architecture

### Frontend Components

```
┌────────────────────────────────────────────────────────┐
│                      App.jsx                           │
│  • State management (results, loading, errors)         │
│  • Component orchestration                             │
│  • Layout structure                                    │
└──────┬──────────────────────────┬──────────────────────┘
       │                          │
       ▼                          ▼
┌──────────────────────┐   ┌──────────────────────────┐
│ SingleUrlAnalyzer    │   │    ResultCard            │
│ ┌──────────────────┐ │   │ ┌──────────────────────┐ │
│ │ URL Input        │ │   │ │ Status Display       │ │
│ │ Example Chips    │ │   │ │ CAPTCHA Warnings     │ │
│ │ Submit Button    │ │   │ │ Component Details    │ │
│ │ Loading State    │ │   │ │ HTML Snippets        │ │
│ └──────────────────┘ │   │ │ AI Analysis          │ │
│                      │   │ │ (Markdown Rendered)  │ │
│ Examples:            │   │ └──────────────────────┘ │
│ • GetCovered         │   │                          │
│ • GitHub             │   │ Features:                │
│ • Instagram          │   │ • Copy to clipboard     │
│ • Stack Overflow     │   │ • Code beautification   │
│ • Etsy               │   │ • Markdown rendering    │
└──────────────────────┘   └──────────────────────────┘
```

### Backend Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   main.py (FastAPI)                     │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Routes:                                           │ │
│  │  • GET  /         - Health check                  │ │
│  │  • POST /analyze  - Main analysis endpoint        │ │
│  │                                                    │ │
│  │  Middleware:                                       │ │
│  │  • CORS (allow all origins for development)       │ │
│  │  • Request logging                                │ │
│  │  • Error handling                                 │ │
│  └───────────────────────────────────────────────────┘ │
└──────┬────────────────────────────┬────────────────────┘
       │                            │
       ▼                            ▼
┌──────────────────────┐    ┌──────────────────────────┐
│  scraper.py          │    │  agent.py                │
│                      │    │                          │
│  AuthDetector        │    │  AgenticAuthDetector     │
│  ┌────────────────┐  │    │  ┌────────────────────┐ │
│  │ ChromeDriver   │  │    │  │ Playwright         │ │
│  │ • Launch       │  │    │  │ • Dynamic click    │ │
│  │ • Navigate     │  │    │  │ • Path navigation  │ │
│  │ • Extract HTML │  │    │  │ • Form detection   │ │
│  │ • Close        │  │    │  └────────────────────┘ │
│  └────────────────┘  │    │  ┌────────────────────┐ │
│  ┌────────────────┐  │    │  │ AI Enhancement     │ │
│  │ BeautifulSoup  │  │    │  │ • Validate results │ │
│  │ • 9 methods    │  │    │  │ • Confidence check │ │
│  │ • Bot detect   │  │    │  └────────────────────┘ │
│  │ • AI analyze   │  │    │                          │
│  └────────────────┘  │    │  Only runs when          │
│                      │    │  use_agents=true         │
└──────────────────────┘    └──────────────────────────┘
```

---

## 🔍 Detection Methods Deep Dive

```
┌─────────────────────────────────────────────────────────┐
│           9 Detection Methods (BeautifulSoup)           │
└─────────────────────────────────────────────────────────┘

Method 1: Traditional HTML Forms
┌──────────────────────────────────────┐
│ <form>                               │
│   <input type="password" />          │
│   <input type="text" />              │
│   <button type="submit">Login</...>  │
│ </form>                              │
└──────────────────────────────────────┘

Method 2: Login Class Detection
┌──────────────────────────────────────┐
│ <form class="login-form">            │
│ <div class="signin-container">       │
│ <section class="auth-section">       │
└──────────────────────────────────────┘

Method 3: Instagram-Style
┌──────────────────────────────────────┐
│ <input name="username" />            │
│ <input name="password" />            │
└──────────────────────────────────────┘

Method 4: WordPress-Style
┌──────────────────────────────────────┐
│ <input name="usernameOrEmail" />     │
│ <input name="user_login" />          │
└──────────────────────────────────────┘

Method 5: ARIA Labels
┌──────────────────────────────────────┐
│ <input aria-label="password" />      │
│ <input aria-label="username" />      │
└──────────────────────────────────────┘

Method 6: Input Combinations
┌──────────────────────────────────────┐
│ Username/Email + Password proximity  │
│ detection within same container      │
└──────────────────────────────────────┘

Method 7: JavaScript Containers
┌──────────────────────────────────────┐
│ <div id="react-login">               │
│ <div class="vue-auth-component">     │
│ <section data-component="auth">      │
└──────────────────────────────────────┘

Method 8: Data Attributes
┌──────────────────────────────────────┐
│ <div data-testid="login-form">       │
│ <button data-qa="signin-button">     │
└──────────────────────────────────────┘

Method 9: Button Context
┌──────────────────────────────────────┐
│ Find login buttons near input fields │
│ Analyze surrounding DOM structure    │
└──────────────────────────────────────┘
```

---

## 🎯 Technology Stack

```
┌──────────────────────────────────────────────────────────┐
│                      Frontend Stack                       │
│  • React 18                  - UI framework              │
│  • Vite 5                    - Build tool                │
│  • TailwindCSS 3             - Styling                   │
│  • react-markdown            - Markdown rendering        │
│  • js-beautify               - Code formatting           │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                      Backend Stack                        │
│  • Python 3.8+               - Programming language      │
│  • FastAPI 0.109+            - Web framework             │
│  • Uvicorn 0.27+             - ASGI server               │
│  • Pydantic 2.10+            - Data validation           │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   Browser Automation                      │
│  • undetected-chromedriver   - Anti-bot ChromeDriver     │
│  • Selenium 4.15+            - WebDriver API             │
│  • Playwright 1.48+          - Dynamic detection (opt)   │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                    HTML Processing                        │
│  • BeautifulSoup4 4.12+      - HTML parsing              │
│  • requests 2.31+            - HTTP client               │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                      AI/ML Stack                          │
│  • Ollama 0.3+               - Local LLM runtime         │
│  • Llama 3.2                 - Language model            │
└──────────────────────────────────────────────────────────┘
```

---

_Last Updated: October 15, 2025_
