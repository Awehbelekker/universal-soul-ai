#!/usr/bin/env python3
"""Quick API test"""

print("🧪 Quick API Test")
print("=" * 30)

# Test OpenAI
try:
    import openai
    client = openai.OpenAI(api_key="your_openai_api_key_here")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'Hello'"}],
        max_tokens=10
    )
    
    print("✅ OpenAI: Working!")
    print(f"   Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ OpenAI failed: {e}")

# Test Google AI
try:
    import google.generativeai as genai
    genai.configure(api_key="AIzaSyASRM4p3n9LokwxNfPtRW5yzy6cxg8ajj4")
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Hello'")
    
    print("✅ Google AI: Working!")
    print(f"   Response: {response.text}")
    
except Exception as e:
    print(f"❌ Google AI failed: {e}")

print("\n🎉 Test complete!")
