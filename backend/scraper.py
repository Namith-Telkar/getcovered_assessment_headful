import requests
from bs4 import BeautifulSoup
import ollama
import json
import re
from urllib.parse import urljoin, urlparse
import asyncio
from playwright.async_api import async_playwright

class AuthDetector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        self.use_playwright = False
    
    def detect_auth_components(self, url, max_depth=2, use_playwright=True):
        """
        Recursively detect auth components with AI guidance
        
        Args:
            url: URL to analyze
            max_depth: Maximum recursion depth for link following
            use_playwright: If True (default), always use Playwright for maximum compatibility.
                          If False, only use Playwright for detected JS-heavy pages.
        """
        if use_playwright:
            print(f"🎭 Using Playwright by default for maximum compatibility...")
            # Return the coroutine directly, let the caller await it
            return self._detect_with_playwright(url)
        
        # Legacy mode: only use Playwright if detected as JS-heavy
        if self._is_js_heavy_page(url):
            print(f"🌐 Detected JS-heavy page dynamically, using Playwright...")
            return self._detect_with_playwright(url)
        
        return self._detect_recursive(url, depth=0, max_depth=max_depth, visited=set())
    
    def _detect_recursive(self, url, depth, max_depth, visited):
        print(f"\n🔍 DEPTH {depth}: Analyzing {url}")
        
        if url in visited:
            print(f"⏭️  Already visited, skipping")
            return {
                "url": url,
                "found": False,
                "components": [],
                "ai_analysis": "URL already visited"
            }
        
        visited.add(url)
        
        try:
            # Step 1: Scrape current page
            print(f"📄 Scraping page...")
            html_content = self._scrape_page(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Step 2: Traditional detection (ALWAYS do this)
            print(f"🔎 Traditional detection...")
            traditional_results = self._traditional_detection(soup)
            print(f"📊 Found {len(traditional_results)} traditional components")
            
            # Step 3: If found, return results
            if traditional_results:
                print(f"✅ Auth components found! Getting AI analysis...")
                ai_analysis = self._ai_analyze_found(html_content, soup)
                print(f"🤖 AI Analysis: {ai_analysis[:100]}...")
                return {
                    "url": url,
                    "found": True,
                    "components": traditional_results,
                    "ai_analysis": ai_analysis
                }
            
            # Step 4: If at max depth, do final AI analysis but don't recurse
            if depth >= max_depth:
                print(f"🛑 Max depth reached, doing final AI analysis...")
                ai_analysis = self._ai_analyze_not_found(soup, [])
                print(f"🤖 Final AI Analysis: {ai_analysis[:100]}...")
                return {
                    "url": url,
                    "found": False,
                    "components": [],
                    "ai_analysis": ai_analysis
                }
            
            # Step 5: If not found and not at max depth, ask AI for potential login links
            print(f"🤖 Asking AI for potential login links...")
            potential_links = self._ai_suggest_login_links(soup, url)
            print(f"🔗 AI suggested {len(potential_links)} links: {potential_links}")
            
            # Step 6: Try each suggested link recursively
            for i, link_url in enumerate(potential_links[:2]):  # Limit to 2 links per level
                if link_url not in visited:
                    print(f"🚀 Following suggested link {i+1}: {link_url}")
                    result = self._detect_recursive(link_url, depth + 1, max_depth, visited)
                    if result["found"]:
                        # Update analysis to show the path taken
                        result["ai_analysis"] = f"Found via link from {url}: {result['ai_analysis']}"
                        return result
                else:
                    print(f"⏭️  Skipping already visited: {link_url}")
            
            # Step 7: No auth found at this level
            print(f"❌ No auth found. Getting final AI analysis...")
            ai_analysis = self._ai_analyze_not_found(soup, potential_links)
            print(f"🤖 Final AI Analysis: {ai_analysis[:100]}...")
            return {
                "url": url,
                "found": False,
                "components": [],
                "ai_analysis": ai_analysis
            }
            
        except Exception as e:
            return {
                "url": url,
                "found": False,
                "components": [],
                "ai_analysis": f"Error: {str(e)}"
            }
    
    def _scrape_page(self, url):
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    
    def _is_js_heavy_page(self, url):
        """
        Dynamically detect if a page is JavaScript-heavy by analyzing initial HTML.
        Returns True if the page likely needs JavaScript rendering.
        """
        try:
            print(f"🔍 Analyzing page to detect if JS-heavy...")
            
            # Quick check for known problematic domains that always need Playwright
            # (Fallback for sites that may have detection issues)
            domain = urlparse(url).netloc.lower()
            known_js_heavy = ['instagram.com', 'twitter.com', 'x.com', 'wordpress.com']
            if any(known in domain for known in known_js_heavy):
                print(f"   ⚡ Known JS-heavy domain detected: {domain}")
                print(f"✅ Page is JS-heavy (known domain), will use Playwright")
                return True
            
            response = self.session.get(url, timeout=10)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            print(f"   📄 HTML size: {len(html)} bytes")
            
            # Indicators that suggest JS-heavy page
            indicators = {
                'minimal_content': 0,
                'many_scripts': 0,
                'react_vue_angular': 0,
                'spa_frameworks': 0,
                'no_forms': 0,
                'placeholder_divs': 0
            }
            
            # 1. Check for minimal HTML content (< 5KB with mostly scripts)
            if len(html) < 5000:
                script_tags = soup.find_all('script')
                if len(script_tags) > 3:
                    indicators['minimal_content'] = 1
                    print(f"   ✓ Minimal HTML with {len(script_tags)} scripts")
            
            # 2. Check for excessive JavaScript (many script tags or large bundles)
            script_tags = soup.find_all('script')
            if len(script_tags) > 10:
                indicators['many_scripts'] = 1
                print(f"   ✓ Many script tags ({len(script_tags)})")
            
            # 3. Check for React/Vue/Angular indicators
            html_lower = html.lower()
            react_indicators = ['react', 'reactdom', '__react', 'data-reactroot', 'data-reactid']
            vue_indicators = ['vue', 'v-app', 'v-if', 'data-v-']
            angular_indicators = ['angular', 'ng-app', 'ng-controller', 'ng-']
            
            framework_count = 0
            if any(indicator in html_lower for indicator in react_indicators):
                framework_count += 1
                print(f"   ✓ React framework detected")
            if any(indicator in html_lower for indicator in vue_indicators):
                framework_count += 1
                print(f"   ✓ Vue framework detected")
            if any(indicator in html_lower for indicator in angular_indicators):
                framework_count += 1
                print(f"   ✓ Angular framework detected")
            
            if framework_count > 0:
                indicators['react_vue_angular'] = 1
            
            # 4. Check for SPA framework patterns
            spa_patterns = ['webpack', 'chunk', 'bundle.js', 'app.js', 'main.js', 'vendor.js']
            script_srcs = [script.get('src', '').lower() for script in script_tags]
            if any(pattern in ' '.join(script_srcs) for pattern in spa_patterns):
                indicators['spa_frameworks'] = 1
                print(f"   ✓ SPA bundle patterns detected")
            
            # 5. Check for lack of traditional forms but presence of login-related content
            forms = soup.find_all('form')
            traditional_inputs = soup.find_all('input', {'type': ['text', 'email', 'password']})
            body_text = soup.get_text().lower() if soup.body else ''
            
            has_login_keywords = any(keyword in body_text for keyword in ['login', 'sign in', 'password', 'username'])
            
            if len(forms) == 0 and len(traditional_inputs) == 0 and has_login_keywords:
                indicators['no_forms'] = 1
                print(f"   ✓ Login keywords present but no traditional forms")
            
            # 6. Check for placeholder divs (root, app, etc.) with minimal children
            root_divs = soup.find_all('div', {'id': re.compile(r'root|app|main|__next', re.I)})
            for root_div in root_divs:
                # If root div exists but has very few direct HTML elements
                children = root_div.find_all(recursive=False)
                if len(children) < 5:
                    indicators['placeholder_divs'] = 1
                    print(f"   ✓ Root div with minimal content (SPA mount point)")
                    break
            
            # Calculate score (out of 6 possible indicators)
            score = sum(indicators.values())
            threshold = 2  # If 2 or more indicators, likely JS-heavy
            
            print(f"📊 JS-heavy score: {score}/6 (threshold: {threshold})")
            
            is_js_heavy = score >= threshold
            
            if is_js_heavy:
                print(f"✅ Page is JS-heavy, will use Playwright")
            else:
                print(f"✅ Page is traditional HTML, will use fast scraping")
            
            return is_js_heavy
            
        except Exception as e:
            print(f"⚠️  Error detecting JS-heavy page, defaulting to traditional: {e}")
            return False
    
    def _needs_playwright(self, url):
        """
        DEPRECATED: Legacy method using domain hardcoding.
        Kept for backwards compatibility but not used.
        """
        js_heavy_domains = [
            'instagram.com',
            'twitter.com',
            'x.com',
            'facebook.com',
            'linkedin.com',
            'tiktok.com',
            'netflix.com',
            'airbnb.com',
            'wordpress.com'
        ]
        domain = urlparse(url).netloc.lower()
        return any(heavy_domain in domain for heavy_domain in js_heavy_domains)
    
    async def _detect_with_playwright(self, url):
        """Use Playwright to render JavaScript and detect auth components"""
        try:
            print(f"🎭 Starting Playwright for {url}")
            playwright = await async_playwright().start()
            
            # Launch with more realistic settings to avoid bot detection
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York'
                # Removed extra_http_headers - they were triggering bot detection!
                # Instagram detects DNT:1 and other headers as bot indicators
            )
            
            page = await context.new_page()
            
            # Hide webdriver property
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            print(f"📄 Navigating to {url}...")
            
            # Use consistent strategy - networkidle works best
            # Instagram's bot detection is TIME-BASED: if you wait too long, it removes the form!
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                # Keep wait time SHORT - Instagram detects bots if page sits idle too long
                await page.wait_for_timeout(5000)  # 5 seconds is the sweet spot
            except Exception as nav_err:
                print(f"⚠️  Navigation warning: {nav_err}")
                # Continue anyway, page might have loaded
            
            # Get HTML content QUICKLY before Instagram's bot detection kicks in
            html_content = await page.content()
            print(f"✅ Got rendered HTML ({len(html_content)} chars)")
            
            # Take screenshot for debugging (optional)
            # await page.screenshot(path='debug_screenshot.png')
            
            await context.close()
            await browser.close()
            await playwright.stop()
            
            # Check if we hit a CAPTCHA or bot protection
            # Be careful: many sites reference "captcha" in their JS configs (like "arkose_captcha")
            # without actually having a CAPTCHA. Only flag if it's an actual CAPTCHA page.
            captcha_detected = False
            html_lower = html_content.lower()
            
            # Specific CAPTCHA indicators (actual blocking challenges, not just references)
            blocking_captcha_indicators = [
                'please verify you are a human',
                'solve this puzzle',
                'press and hold',
                'datadome',  # DataDome is always an actual blocker
                'perimeterx',  # PerimeterX is always an actual blocker
                'cf-challenge',  # Cloudflare challenge page
                'challenge-platform',  # Generic challenge
                '<title>just a moment...</title>',  # Cloudflare
                'ray id:',  # Cloudflare blocked page
            ]
            
            for indicator in blocking_captcha_indicators:
                if indicator in html_lower:
                    captcha_detected = True
                    print(f"🚫 Bot protection detected: '{indicator}' found in page")
                    break
            
            # If page is very small (< 3KB) and contains generic captcha keywords, it's likely blocked
            if not captcha_detected and len(html_content) < 3000:
                generic_captcha_keywords = ['recaptcha', 'hcaptcha', 'captcha-box', 'g-recaptcha']
                for keyword in generic_captcha_keywords:
                    if keyword in html_lower:
                        captcha_detected = True
                        print(f"🚫 Small page with CAPTCHA element: '{keyword}' found")
                        break
            
            # If CAPTCHA detected and page is very small, it's likely blocked
            if captcha_detected and len(html_content) < 3000:
                print(f"⚠️  Page blocked by anti-bot protection")
                return {
                    "url": url,
                    "found": False,
                    "components": [],
                    "captcha_detected": True,
                    "ai_analysis": (
                        "🚫 **Site Protected by Anti-Bot Service**\n\n"
                        "This website uses CAPTCHA or anti-bot protection (DataDome, Cloudflare, etc.) "
                        "that prevents automated scraping. The login page cannot be accessed programmatically.\n\n"
                        "**Alternatives:**\n"
                        "- Use the site's official API if available\n"
                        "- Manually export HTML from your browser\n"
                        "- Test with similar sites that don't have bot protection\n\n"
                        "See CAPTCHA_PROTECTED_SITES.md for more details and workarounds."
                    )
                }
            
            # Now analyze the rendered HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Debug: Check if inputs are in HTML before parsing
            raw_username_count = html_content.count('name="username"')
            raw_password_count = html_content.count('name="password"')
            print(f"🔍 Raw HTML check: username={raw_username_count}, password={raw_password_count}")
            
            components = self._traditional_detection(soup)
            
            if components:
                print(f"✅ Found {len(components)} auth components with Playwright")
                ai_analysis = self._ai_analyze_found(html_content, soup)
                return {
                    "url": url,
                    "found": True,
                    "components": components,
                    "ai_analysis": f"[Playwright Rendered] {ai_analysis}"
                }
            else:
                print(f"❌ No auth components found even with Playwright")
                
                # If CAPTCHA detected, mention it in the analysis
                if captcha_detected:
                    ai_analysis = (
                        "Page rendered but may be partially blocked by anti-bot protection. "
                        "No auth components detected. The site may require manual access or "
                        "the login form may be behind additional security checks."
                    )
                else:
                    ai_analysis = self._ai_analyze_not_found(soup, [])
                
                return {
                    "url": url,
                    "found": False,
                    "components": [],
                    "ai_analysis": f"[Playwright Rendered] {ai_analysis}"
                }
                
        except Exception as e:
            print(f"❌ Playwright error: {e}")
            return {
                "url": url,
                "found": False,
                "components": [],
                "ai_analysis": f"Playwright error: {str(e)}"
            }
    
    def _traditional_detection(self, soup):
        components = []
        html_source = str(soup)
        
        # 1. Traditional HTML forms with password inputs
        password_inputs = soup.find_all('input', {'type': 'password'})
        for pwd_input in password_inputs:
            form = pwd_input.find_parent('form')
            if form:
                components.append({
                    'type': 'html_login_form',
                    'html': str(form),
                    'method': 'traditional_html'
                })
                print(f"   ✓ Found HTML form with password input")
        
        # 2. Forms with login/signin classes
        login_forms = soup.find_all('form', {'class': re.compile(r'login|signin|auth', re.I)})
        for form in login_forms:
            components.append({
                'type': 'html_login_form',
                'html': str(form),
                'method': 'traditional_html'
            })
            print(f"   ✓ Found form with login class")
        
        # 3. Instagram-specific: Look for input elements with name="username" and name="password"
        username_inputs = soup.find_all('input', {'name': 'username'})
        password_inputs_by_name = soup.find_all('input', {'name': 'password'})
        
        print(f"🔍 Instagram detection: username inputs={len(username_inputs)}, password inputs={len(password_inputs_by_name)}")
        
        if username_inputs and password_inputs_by_name:
            # Find the common parent container
            for username_input in username_inputs:
                parent = username_input.find_parent(['form', 'div', 'section'])
                if parent:
                    components.append({
                        'type': 'instagram_style_login',
                        'html': str(parent),
                        'method': 'instagram_detection'
                    })
                    print(f"   ✓ Found Instagram-style login (username + password inputs)")
                    break
        else:
            if username_inputs or password_inputs_by_name:
                print(f"   ⚠️  Partial match: username={len(username_inputs)}, password={len(password_inputs_by_name)}")
        
        # 4. WordPress-specific: Look for usernameOrEmail field
        wordpress_inputs = soup.find_all('input', {'name': re.compile(r'usernameOrEmail|user_login|log', re.I)})
        if wordpress_inputs:
            for wp_input in wordpress_inputs:
                parent = wp_input.find_parent(['form', 'div', 'section', 'main'])
                if parent:
                    # Check if there's also a password field nearby
                    password_fields = parent.find_all('input', {'type': 'password'})
                    if password_fields or 'password' in str(parent).lower():
                        components.append({
                            'type': 'wordpress_style_login',
                            'html': str(parent),
                            'method': 'wordpress_detection'
                        })
                        print(f"   ✓ Found WordPress-style login (usernameOrEmail field)")
                        break
        
        # 5. Look for aria-label password fields (common in React apps like Instagram)
        aria_password_inputs = soup.find_all('input', {'aria-label': re.compile(r'password', re.I)})
        for pwd_input in aria_password_inputs:
            parent = pwd_input.find_parent(['form', 'div', 'section'])
            if parent:
                components.append({
                    'type': 'aria_labeled_password',
                    'html': str(parent),
                    'method': 'aria_label_detection'
                })
                print(f"   ✓ Found password field with aria-label")
        
        # 6. Detect all input fields and check if there's a combination suggesting login
        all_inputs = soup.find_all('input')
        input_types = [inp.get('type', '').lower() for inp in all_inputs]
        input_names = [inp.get('name', '').lower() for inp in all_inputs]
        
        # Check for username/email + password combination (expanded list)
        has_username = any(name in input_names for name in ['username', 'email', 'user', 'login', 'usernameoremail', 'user_login', 'log'])
        has_password = 'password' in input_types or 'password' in input_names
        
        if has_username and has_password and len(components) == 0:
            # Find container with these inputs
            for inp in all_inputs:
                if inp.get('name', '').lower() in ['username', 'email', 'password']:
                    parent = inp.find_parent(['div', 'section', 'form', 'main'])
                    if parent:
                        components.append({
                            'type': 'detected_login_inputs',
                            'html': str(parent),
                            'method': 'input_combination_detection'
                        })
                        print(f"   ✓ Found username + password input combination")
                        break
        
        # 7. JavaScript/React-based forms - container detection
        potential_forms = soup.find_all(['div', 'section', 'main'], {'class': True})
        for container in potential_forms:
            classes = ' '.join(container.get('class', [])).lower()
            
            # Check if container has auth-related classes
            if any(keyword in classes for keyword in ['login', 'signin', 'auth', 'form']):
                inputs = container.find_all(['input', 'div'], {'type': True})
                if len(inputs) >= 2:  # Likely username + password
                    components.append({
                        'type': 'js_auth_container',
                        'html': str(container),
                        'method': 'javascript_container'
                    })
                    print(f"   ✓ Found JS auth container with {len(inputs)} inputs")
        
        # 8. Data attributes for test/automation (common in React apps)
        auth_data_elements = soup.find_all(attrs={'data-testid': re.compile(r'login|signin|auth|password', re.I)})
        for elem in auth_data_elements:
            parent = elem.find_parent(['div', 'section', 'form'])
            if parent:
                components.append({
                    'type': 'data_attr_auth',
                    'html': str(parent),
                    'method': 'data_attributes'
                })
                print(f"   ✓ Found element with auth data-testid")
        
        # 9. Button context - login buttons near inputs
        auth_buttons = soup.find_all(['button', 'div'], string=re.compile(r'sign\s*in|log\s*in|login', re.I))
        for button in auth_buttons:
            parent = button.find_parent(['div', 'section', 'form'])
            if parent:
                nearby_inputs = parent.find_all(['input'], {'type': True})
                if len(nearby_inputs) >= 1:
                    components.append({
                        'type': 'button_with_inputs',
                        'html': str(parent),
                        'method': 'button_context'
                    })
                    print(f"   ✓ Found login button with {len(nearby_inputs)} nearby inputs")
        
        print(f"🔍 Detection found: {len(components)} components")
        return components
    
    def _ai_suggest_login_links(self, soup, base_url):
        """Ask AI to analyze complete page content for any auth-related elements"""
        try:
            # Get FULL page content including CSS and JS
            full_html = str(soup)
            
            # Extract all clickable elements with their full context
            all_elements = []
            
            # Get ALL links
            for link in soup.find_all('a', href=True):
                text = link.get_text().strip()
                href = link.get('href')
                classes = ' '.join(link.get('class', []))
                onclick = link.get('onclick', '')
                all_elements.append(f"<a href='{href}' class='{classes}' onclick='{onclick}'>{text}</a>")
            
            # Get ALL buttons and inputs
            for elem in soup.find_all(['button', 'input', 'div'], {'type': True}):
                text = elem.get_text().strip()
                elem_type = elem.get('type', '')
                classes = ' '.join(elem.get('class', []))
                onclick = elem.get('onclick', '')
                data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
                all_elements.append(f"<{elem.name} type='{elem_type}' class='{classes}' onclick='{onclick}' data='{data_attrs}'>{text}</{elem.name}>")
            
            # Get divs that might be clickable (React components, etc.)
            for div in soup.find_all('div', {'class': True}):
                classes = ' '.join(div.get('class', []))
                if any(keyword in classes.lower() for keyword in ['login', 'signin', 'auth', 'button', 'click']):
                    text = div.get_text().strip()[:50]
                    onclick = div.get('onclick', '')
                    data_attrs = {k: v for k, v in div.attrs.items() if k.startswith('data-')}
                    all_elements.append(f"<div class='{classes}' onclick='{onclick}' data='{data_attrs}'>{text}</div>")
            
            print(f"📝 Sending FULL page content to AI ({len(full_html)} chars)")
            print(f"📝 Found {len(all_elements)} potentially clickable elements")
            
            # If no elements found, try common auth URLs as fallback
            if len(all_elements) == 0:
                print("⚠️  No clickable elements found, trying common auth URLs...")
                domain = urlparse(base_url).netloc.lower()
                common_auth_paths = []
                
                if 'amazon' in domain:
                    common_auth_paths = ['/ap/signin', '/gp/signin', '/signin']
                elif 'twitter' in domain or 'x.com' in domain:
                    common_auth_paths = ['/login', '/i/flow/login']
                elif 'facebook' in domain:
                    common_auth_paths = ['/login', '/login.php']
                elif 'google' in domain:
                    common_auth_paths = ['/accounts/signin', '/signin']
                else:
                    common_auth_paths = ['/login', '/signin', '/auth', '/account/login']
                
                fallback_urls = [urljoin(base_url, path) for path in common_auth_paths]
                print(f"🔧 Trying fallback URLs: {fallback_urls}")
                return fallback_urls[:3]
            
            response = ollama.chat(model='llama3.2:latest', messages=[{
                'role': 'user',
                'content': f'''Find authentication/login URLs from these page elements:

{chr(10).join(all_elements[:15])}

Look for ANY of these patterns:
- Text: "Sign In", "Sign in", "Login", "Log In", "Account", "Your Account"
- URLs: "/signin", "/login", "/ap/signin", "/gp/signin", "/auth", "/account"
- Buttons that might trigger login (even if text doesn't say login)
- Links to account/profile pages

IMPORTANT: Even if text doesn't explicitly say "login", include URLs that could lead to authentication.

Return ONLY JSON array: ["url1", "url2"]'''
            }])
            
            ai_response = response['message']['content'].strip()
            print(f"🤖 AI Full Analysis Response: {ai_response}")
            
            # Extract URLs from AI response
            try:
                # Clean up the response to handle mixed quotes
                cleaned_response = ai_response.replace("'", '"')
                start = cleaned_response.find('[')
                end = cleaned_response.rfind(']') + 1
                if start >= 0 and end > start:
                    json_str = cleaned_response[start:end]
                    print(f"🔧 Cleaned JSON: {json_str}")
                    urls = json.loads(json_str)
                    final_urls = [urljoin(base_url, url) for url in urls if isinstance(url, str)][:3]
                    print(f"✅ AI Extracted URLs from full analysis: {final_urls}")
                    return final_urls
            except Exception as e:
                print(f"❌ Failed to parse AI JSON: {e}")
                # Fallback: extract URLs manually using regex
                import re
                url_pattern = r'["\']([^"\']*(?:login|signin|auth)[^"\']*)["\']'
                matches = re.findall(url_pattern, ai_response, re.IGNORECASE)
                if matches:
                    fallback_urls = [urljoin(base_url, url) for url in matches[:3]]
                    print(f"🔧 Fallback extracted URLs: {fallback_urls}")
                    return fallback_urls
            
            return []
            
        except Exception as e:
            print(f"❌ AI full analysis failed: {e}")
            return []
    
    def _ai_analyze_found(self, html_content, soup):
        """AI analysis when auth components are found"""
        try:
            response = ollama.chat(model='llama3.2:latest', messages=[{
                'role': 'user',
                'content': f'''Authentication components found! Analyze what type of login system this is:

HTML sample: {html_content[:1500]}

Briefly describe:
1. Type of authentication (form-based, modal, etc.)
2. What fields are present
3. Any special features'''
            }])
            return response['message']['content']
        except:
            return "Auth components detected via traditional parsing"
    
    def _ai_analyze_not_found(self, soup, suggested_links):
        """AI analysis when no auth components found"""
        try:
            page_title = soup.find('title')
            title_text = page_title.get_text() if page_title else "No title"
            
            response = ollama.chat(model='llama3.2:latest', messages=[{
                'role': 'user',
                'content': f'''No authentication components found on page: "{title_text}"

Suggested links checked: {suggested_links}

Briefly explain:
1. Why this page might not have login forms
2. What type of page this appears to be
3. Whether login might be handled differently (JS, modals, etc.)'''
            }])
            return response['message']['content']
        except:
            return f"No auth components found. Checked {len(suggested_links)} suggested links."
