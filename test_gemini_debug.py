#!/usr/bin/env python3
"""Debug Gemini API integration"""

import os
import sys
import json
import urllib.request
sys.path.insert(0, '.')

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {bool(api_key)}")
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")

# Test direct API call
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

headers = {
    "Content-Type": "application/json"
}

data = {
    "contents": [
        {
            "parts": [
                {"text": "Analyze the sentiment of this text and respond with just one word: positive, negative, or neutral. Text: I love this!"}
            ]
        }
    ],
    "generationConfig": {
        "maxOutputTokens": 50,
        "temperature": 0.7
    }
}

print("\nMaking direct API call to Gemini...")
print(f"URL: {url[:80]}...")

try:
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("\nAPI Response received!")
        print(json.dumps(result, indent=2))
        
        # Extract text from response
        if 'candidates' in result and len(result['candidates']) > 0:
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"\nExtracted text: {text}")
        
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    print(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")