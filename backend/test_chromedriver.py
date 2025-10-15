#!/usr/bin/env python3
"""
Test script to verify undetected-chromedriver installation and authentication detection.
"""

from scraper import AuthDetector

def test_basic_detection():
    """Test basic authentication detection on Instagram"""
    print("🧪 Testing Authentication Detection with undetected-chromedriver\n")
    print("=" * 70)
    
    detector = AuthDetector()
    
    # Test URL
    test_url = "https://www.instagram.com/accounts/login/"
    print(f"📍 Testing URL: {test_url}")
    print("\n⏳ Chrome browser will open visibly...")
    print("   - Browser navigates to Instagram")
    print("   - Waits 5 seconds for page to load")
    print("   - Extracts HTML")
    print("   - Closes automatically\n")
    
    try:
        # Run detection
        result = detector.detect_auth_components(test_url, use_chromedriver=True)
        
        print("\n" + "=" * 70)
        print("📊 RESULTS")
        print("=" * 70)
        
        print(f"\n✅ Authentication components found: {result['found']}")
        print(f" Number of components: {len(result['components'])}")
        
        if result['components']:
            print("\n📝 Detected Components:")
            for i, component in enumerate(result['components'], 1):
                print(f"\n   Component {i}:")
                print(f"   - Type: {component['type']}")
                print(f"   - Method: {component['method']}")
                html_preview = component['html'][:200] + "..." if len(component['html']) > 200 else component['html']
                print(f"   - HTML Preview: {html_preview}")
        
        if result.get('ai_analysis'):
            print(f"\n🤖 AI Analysis:\n{result['ai_analysis'][:300]}...")
        
        print("\n" + "=" * 70)
        print("✅ Test completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ERROR OCCURRED")
        print("=" * 70)
        print(f"\n{str(e)}\n")
        raise

if __name__ == "__main__":
    test_basic_detection()
