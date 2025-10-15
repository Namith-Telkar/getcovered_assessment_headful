from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from scraper import AuthDetector
from agent import AgenticAuthDetector
import logging

app = FastAPI(title="Auth Component Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = AuthDetector()

class URLRequest(BaseModel):
    url: str
    use_agents: bool = False

class AuthResponse(BaseModel):
    url: str
    found: bool
    components: list
    ai_analysis: str
    method: str = "static"
    captcha_detected: bool = False
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Auth Component Detector API with Agentic Enhancement"}

@app.post("/analyze")
async def analyze_url(request: URLRequest):
    try:
        # Use Playwright for all requests by default (maximum compatibility)
        static_result = detector.detect_auth_components(request.url, use_playwright=True)
        
        # Check if result is a coroutine (Playwright mode)
        import inspect
        if inspect.iscoroutine(static_result):
            static_result = await static_result
        
        # Log HTML snippet length for debugging
        if static_result.get('components'):
            for i, comp in enumerate(static_result['components']):
                html_len = len(comp.get('html', ''))
                print(f"📏 Component {i+1}: HTML length = {html_len} characters")
        
        if request.use_agents:
            # Use agentic approach
            agent_detector = AgenticAuthDetector()
            result = await agent_detector.detect_with_agents(request.url, static_result['components'])
            
            return {
                "url": request.url,
                "found": len(result['components']) > 0,
                "components": result['components'],
                "ai_analysis": result.get('ai_analysis', ''),
                "method": result['method'],
                "captcha_detected": static_result.get('captcha_detected', False),
                "error": None
            }
        else:
            # Return static results
            return {
                "url": static_result['url'],
                "found": static_result['found'],
                "components": static_result['components'],
                "ai_analysis": static_result['ai_analysis'],
                "method": "static",
                "captcha_detected": static_result.get('captcha_detected', False),
                "error": static_result.get('error')
            }
            
    except Exception as e:
        logging.error(f"Error analyzing {request.url}: {str(e)}")
        return {
            "url": request.url,
            "found": False,
            "components": [],
            "ai_analysis": "",
            "method": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
