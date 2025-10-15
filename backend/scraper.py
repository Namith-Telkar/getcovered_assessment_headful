import requests
from bs4 import BeautifulSoup
import ollama
import json
import re
from urllib.parse import urljoin, urlparse
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    
    def detect_auth_components(self, url, use_chromedriver=True):
        """
        Detect auth components using undetected-chromedriver
        
        Args:
            url: URL to analyze
            use_chromedriver: If True (default), use undetected-chromedriver to open in browser
        """
        if use_chromedriver:
            print(f"🚗 Using undetected-chromedriver to open page in browser...")
            return self._detect_with_chromedriver(url)
        
        # Fallback: simple scraping without ChromeDriver
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            components = self._traditional_detection(soup)
            
            if components:
                ai_analysis = self._ai_analyze_found(html_content, soup)
                return {
                    "url": url,
                    "found": True,
                    "components": components,
                    "ai_analysis": ai_analysis
                }
            else:
                ai_analysis = self._ai_analyze_not_found(soup, [])
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
    
    
    def _detect_with_chromedriver(self, url):
        """Use undetected-chromedriver to open page in browser and extract HTML"""
        driver = None
        try:
            print(f"🚗 Starting undetected-chromedriver for {url}")
            
            # Create options for Chrome
            options = uc.ChromeOptions()
            # Set to headless=False to see the browser window
            # options.add_argument('--headless=new')  # Comment this out to see the browser
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--start-maximized')
            
            # Initialize undetected chromedriver
            driver = uc.Chrome(options=options, version_main=None)
            
            print(f"📄 Navigating to {url}...")
            try:
                driver.get(url)
            except Exception as nav_err:
                print(f"❌ Navigation failed: {nav_err}")
                raise Exception(f"Failed to navigate to URL: {str(nav_err)}")
            
            # Wait for page to load
            print(f"⏳ Waiting for page to load...")
            time.sleep(5)  # Wait 5 seconds for dynamic content to load
            
            # Check if browser window is still open
            try:
                current_url = driver.current_url
                print(f"✅ Browser still active, current URL: {current_url}")
            except Exception as check_err:
                print(f"⚠️  Browser window closed unexpectedly (likely anti-bot protection): {check_err}")
                raise Exception("Browser window was closed by the website (anti-bot protection detected)")
            
            # Get the page source immediately (before any waits that might fail)
            try:
                html_content = driver.page_source
                print(f"✅ Got rendered HTML ({len(html_content)} chars)")
            except Exception as html_err:
                print(f"❌ Failed to get page source: {html_err}")
                raise Exception(f"Could not extract HTML: {str(html_err)}")
            
            # Optional: Wait for specific elements (but don't fail if it errors)
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as wait_err:
                print(f"⚠️  Wait warning (continuing anyway): {wait_err}")
            
            # Take screenshot for debugging (optional)
            # driver.save_screenshot('debug_screenshot.png')
            
            # Check if we hit a CAPTCHA or bot protection
            captcha_detected = False
            html_lower = html_content.lower()
            
            blocking_captcha_indicators = [
                'please verify you are a human',
                'solve this puzzle',
                'press and hold',
                'datadome',
                'perimeterx',
                'cf-challenge',
                'challenge-platform',
                '<title>just a moment...</title>',
                'ray id:',
            ]
            
            for indicator in blocking_captcha_indicators:
                if indicator in html_lower:
                    captcha_detected = True
                    print(f"🚫 Bot protection detected: '{indicator}' found in page")
                    break
            
            if not captcha_detected and len(html_content) < 3000:
                generic_captcha_keywords = ['recaptcha', 'hcaptcha', 'captcha-box', 'g-recaptcha']
                for keyword in generic_captcha_keywords:
                    if keyword in html_lower:
                        captcha_detected = True
                        print(f"🚫 Small page with CAPTCHA element: '{keyword}' found")
                        break
            
            if captcha_detected and len(html_content) < 3000:
                print(f"⚠️  Page blocked by anti-bot protection")
                driver.quit()
                return {
                    "url": url,
                    "found": False,
                    "components": [],
                    "captcha_detected": True,
                    "ai_analysis": (
                        "🚫 **Site Protected by Anti-Bot Service**\n\n"
                        "This website uses CAPTCHA or anti-bot protection that prevents automated scraping. "
                        "The login page cannot be accessed programmatically.\n\n"
                        "**Alternatives:**\n"
                        "- Use the site's official API if available\n"
                        "- Manually export HTML from your browser\n"
                        "- Test with similar sites that don't have bot protection"
                    )
                }
            
            # Now analyze the rendered HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Debug: Check if inputs are in HTML before parsing
            raw_username_count = html_content.count('name="username"')
            raw_password_count = html_content.count('name="password"')
            print(f"🔍 Raw HTML check: username={raw_username_count}, password={raw_password_count}")
            
            components = self._traditional_detection(soup)
            
            # Close the browser safely
            try:
                if driver:
                    driver.quit()
                    print(f"✅ Browser closed successfully")
            except Exception as close_err:
                print(f"⚠️  Browser close warning (browser may have already closed): {close_err}")
            
            if components:
                print(f"✅ Found {len(components)} auth components")
                ai_analysis = self._ai_analyze_found(html_content, soup)
                return {
                    "url": url,
                    "found": True,
                    "components": components,
                    "ai_analysis": f"[ChromeDriver Rendered] {ai_analysis}"
                }
            else:
                print(f"❌ No auth components found")
                
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
                    "ai_analysis": f"[ChromeDriver Rendered] {ai_analysis}"
                }
                
        except Exception as e:
            print(f"❌ ChromeDriver error: {e}")
            # Try to close the browser if it's still open
            try:
                if driver:
                    driver.quit()
                    print(f"✅ Browser closed after error")
            except Exception as close_err:
                print(f"⚠️  Could not close browser (may already be closed): {close_err}")
            
            return {
                "url": url,
                "found": False,
                "components": [],
                "ai_analysis": f"ChromeDriver error: {str(e)}"
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
