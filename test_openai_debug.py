#!/usr/bin/env python3
"""Debug OpenAI API integration"""

import os
import sys
import json
import urllib.request
sys.path.insert(0, '.')

api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key found: {bool(api_key)}")
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")

# Test direct API call
url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Analyze the sentiment of this text and respond with just one word: positive, negative, or neutral. Text: I love this!"}
    ],
    "max_tokens": 50,
    "temperature": 0.7
}

print("\nMaking direct API call to OpenAI...")
print(f"URL: {url}")

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
        if 'choices' in result and len(result['choices']) > 0:
            text = result['choices'][0]['message']['content']
            print(f"\nExtracted text: {text}")
        
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    print(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")