import asyncio
from playwright.async_api import async_playwright
import ollama
import json
from typing import List, Dict, Any

class AgenticAuthDetector:
    def __init__(self):
        pass
        
    async def detect_with_agents(self, url: str, static_components: List[Dict]) -> Dict[str, Any]:
        """Orchestrate detection using multiple agents"""
        
        # If static detection found components, enhance with validation
        if static_components:
            return await self._enhance_static_results(url, static_components)
        
        # If static failed, use dynamic agents
        return await self._dynamic_detection_flow(url)
    
    async def _enhance_static_results(self, url: str, components: List[Dict]) -> Dict[str, Any]:
        """Enhance static results with AI validation"""
        try:
            validation_prompt = f"""
            Analyze these detected auth components from {url}:
            {json.dumps(components, indent=2)}
            
            Are these likely functional login forms? Rate confidence 1-10 and explain briefly.
            """
            
            response = ollama.chat(model='llama3.2:latest', messages=[{
                'role': 'user', 
                'content': validation_prompt
            }])
            
            return {
                'components': components,
                'ai_analysis': response['message']['content'],
                'method': 'static_enhanced'
            }
            
        except Exception as e:
            return {
                'components': components,
                'ai_analysis': f"Validation error: {e}",
                'method': 'static_only'
            }
    
    async def _dynamic_detection_flow(self, url: str) -> Dict[str, Any]:
        """Dynamic detection flow for failed static detection"""
        all_components = []
        
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            # Try dynamic interaction
            dynamic_components = await self._dynamic_detect(context, url)
            all_components.extend(dynamic_components)
            
            # Try navigation if dynamic failed
            if not dynamic_components:
                nav_components = await self._navigate_to_auth(context, url)
                all_components.extend(nav_components)
            
            await context.close()
            await browser.close()
            await playwright.stop()
            
        except Exception as e:
            print(f"Dynamic detection error: {e}")
        
        # AI analysis of dynamic results
        if all_components:
            try:
                analysis_prompt = f"""
                Analyze these dynamically detected auth components from {url}:
                {json.dumps(all_components, indent=2)}
                
                Summarize the authentication method and key findings.
                """
                
                response = ollama.chat(model='llama3.2:latest', messages=[{
                    'role': 'user',
                    'content': analysis_prompt
                }])
                
                return {
                    'components': all_components,
                    'ai_analysis': response['message']['content'],
                    'method': 'dynamic_agents'
                }
                
            except Exception as e:
                return {
                    'components': all_components,
                    'ai_analysis': f"Analysis error: {e}",
                    'method': 'dynamic_only'
                }
        
        return {
            'components': [],
            'ai_analysis': "No authentication components found through dynamic detection",
            'method': 'dynamic_failed'
        }

    async def _dynamic_detect(self, context, url: str) -> List[Dict[str, Any]]:
        """Dynamic detection using browser automation"""
        components = []
        
        try:
            page = await context.new_page()
            await page.goto(url, wait_until='networkidle', timeout=15000)
            
            # Strategy 1: Look for auth-related buttons/links to click
            auth_selectors = [
                'text=/sign.?in/i',
                'text=/log.?in/i', 
                'text=/login/i',
                '[data-testid*="login"]',
                '[class*="login"]'
            ]
            
            for selector in auth_selectors:
                try:
                    elements = await page.locator(selector).all()
                    for element in elements[:2]:  # Limit attempts
                        await element.click(timeout=3000)
                        await page.wait_for_timeout(2000)
                        
                        # Check if auth form appeared
                        forms = await page.locator('form, [data-testid*="login"], [class*="login"]').all()
                        for form in forms:
                            html = await form.inner_html()
                            if any(keyword in html.lower() for keyword in ['password', 'email', 'username']):
                                components.append({
                                    'type': 'dynamic_auth_form',
                                    'html': html[:500] + "...",
                                    'method': 'dynamic_interaction'
                                })
                                break
                        
                        if components:
                            break
                    if components:
                        break
                        
                except Exception:
                    continue
            
            await page.close()
            
        except Exception as e:
            print(f"Dynamic detect error: {e}")
            
        return components

    async def _navigate_to_auth(self, context, url: str) -> List[Dict[str, Any]]:
        """Navigate to likely auth pages"""
        components = []
        auth_paths = ['/login', '/signin', '/sign-in', '/auth', '/account/login']
        
        try:
            page = await context.new_page()
            
            for path in auth_paths:
                try:
                    auth_url = url.rstrip('/') + path
                    response = await page.goto(auth_url, wait_until='networkidle', timeout=10000)
                    
                    if response and response.status == 200:
                        # Check if this page has auth forms
                        forms = await page.locator('form, input[type="password"]').all()
                        if forms:
                            html = await page.content()
                            components.append({
                                'type': 'navigated_auth_page',
                                'html': html[:1000] + "...",
                                'method': 'path_navigation',
                                'url': auth_url
                            })
                            break
                            
                except Exception:
                    continue
                    
            await page.close()
            
        except Exception as e:
            print(f"Navigation error: {e}")
            
        return components
