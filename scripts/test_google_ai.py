#!/usr/bin/env python3
"""
Test Google AI Gemini API specifically
"""

import google.generativeai as genai

# Configure with your API key
genai.configure(api_key="AIzaSyASRM4p3n9LokwxNfPtRW5yzy6cxg8ajj4")

try:
    # List available models
    print("🔍 Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  ✅ {model.name}")
    
    print("\n🧪 Testing Gemini...")
    
    # Try the most common model
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Hello from Gemini!'")
    
    print(f"✅ Google AI Gemini: Connection successful")
    print(f"   Response: {response.text}")
    
except Exception as e:
    print(f"❌ Error: {e}")
