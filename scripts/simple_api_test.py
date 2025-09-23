#!/usr/bin/env python3
"""
Simple API Test for Universal Soul AI
====================================

Quick test of API connections with the configured keys.
"""

import asyncio
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent

def load_api_keys():
    """Load API keys from environment file"""
    api_keys = {}
    api_keys_file = project_root / "android_overlay" / "api_keys.env"
    
    if api_keys_file.exists():
        with open(api_keys_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if value and value != "your_api_key_here":
                        api_keys[key] = value
    
    return api_keys

async def test_anthropic():
    """Test Anthropic Claude API"""
    api_keys = load_api_keys()
    anthropic_key = api_keys.get("ANTHROPIC_API_KEY")
    
    if not anthropic_key:
        print("❌ Anthropic API key not found")
        return False
    
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=anthropic_key)
        
        # Test with a simple message
        message = client.messages.create(
            model="claude-3-haiku-20240307",  # Use cheaper model for testing
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": "Say 'Hello'"
            }]
        )
        
        if message.content and message.content[0].text:
            print("✅ Anthropic Claude: Connection successful")
            print(f"   Response: {message.content[0].text}")
            return True
        else:
            print("❌ Anthropic Claude: Invalid response")
            return False
            
    except Exception as e:
        print(f"❌ Anthropic Claude connection failed: {e}")
        return False

async def test_google_ai():
    """Test Google AI Gemini API"""
    api_keys = load_api_keys()
    google_key = api_keys.get("GOOGLE_AI_API_KEY")
    
    if not google_key:
        print("❌ Google AI API key not found")
        return False
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=google_key)
        
        # Test with a simple generation - try different model names
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Say 'Hello'")
        except:
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content("Say 'Hello'")
            except:
                model = genai.GenerativeModel('models/gemini-pro')
                response = model.generate_content("Say 'Hello'")
        
        if response.text:
            print("✅ Google AI Gemini: Connection successful")
            print(f"   Response: {response.text}")
            return True
        else:
            print("❌ Google AI Gemini: Invalid response")
            return False
            
    except Exception as e:
        print(f"❌ Google AI Gemini connection failed: {e}")
        return False

async def test_openai():
    """Test OpenAI GPT API"""
    api_keys = load_api_keys()
    openai_key = api_keys.get("OPENAI_API_KEY")
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured")
        return False
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=openai_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            messages=[{
                "role": "user",
                "content": "Say 'Hello'"
            }],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ OpenAI GPT: Connection successful")
            print(f"   Response: {response.choices[0].message.content}")
            return True
        else:
            print("❌ OpenAI GPT: Invalid response")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI GPT connection failed: {e}")
        return False

async def main():
    """Main test function"""
    
    print("🧪 Universal Soul AI - Simple API Test")
    print("=" * 50)
    
    # Load API keys
    api_keys = load_api_keys()
    print(f"📋 Loaded {len(api_keys)} API keys")
    
    # Test each API
    results = {}
    
    print("\n🧠 Testing AI Providers:")
    print("-" * 30)
    
    results["anthropic"] = await test_anthropic()
    results["google_ai"] = await test_google_ai()
    results["openai"] = await test_openai()
    
    # Summary
    working_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n📊 Results: {working_count}/{total_count} providers working")
    
    if working_count >= 2:
        print("🎉 Multi-modal AI ready for deployment!")
        print("✅ You have enough working providers for beta testing")
    elif working_count >= 1:
        print("⚠️ Limited functionality available")
        print("💡 Consider adding more API keys for better performance")
    else:
        print("❌ No working providers")
        print("🔧 Please configure valid API keys")
    
    print("\n🚀 Next steps:")
    if working_count >= 1:
        print("  • Run full deployment: python scripts/deploy_beta.py")
        print("  • Test multi-modal demo: python examples/multimodal_ai_demo.py")
    else:
        print("  • Add valid API keys to android_overlay/api_keys.env")
        print("  • Follow setup guide: deployment/api_setup_guide.md")

if __name__ == "__main__":
    asyncio.run(main())
