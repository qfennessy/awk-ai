#!/usr/bin/env python3
"""Test script to verify Gemini API integration"""

import os
import sys
sys.path.insert(0, '.')

# Force Gemini provider
os.environ['PYAWK_AI_PROVIDER'] = 'gemini'
# Temporarily disable other providers
anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
openai_key = os.environ.get('OPENAI_API_KEY', '')
os.environ['ANTHROPIC_API_KEY'] = ''
os.environ['OPENAI_API_KEY'] = ''

from ai_providers import get_ai_provider, reset_provider, GeminiProvider

# Reset to force re-detection
reset_provider()

# Create Gemini provider directly
print("Testing Gemini API Integration...")
print("=" * 50)

# Try direct instantiation
try:
    provider = GeminiProvider()
    print(f"Gemini API Key available: {bool(provider.api_key)}")
    print(f"Active provider: {provider.__class__.__name__}")
except Exception as e:
    print(f"Error creating Gemini provider: {e}")
    sys.exit(1)

# Test sentiment analysis
print("\nSentiment Analysis Tests:")
print("-" * 30)
test_texts = [
    "I absolutely love this product!",
    "This is terrible and disappointing",
    "The weather is cloudy today"
]

for text in test_texts:
    prompt = f"Analyze the sentiment of this text and respond with just one word: positive, negative, or neutral. Text: {text}"
    try:
        result = provider.call_api(prompt, 50)
        print(f"Text: {text[:30]}...")
        print(f"Result: {result}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

# Test classification
print("Classification Test:")
print("-" * 30)
text = "Scientists discover new species in the ocean"
prompt = f"Classify this text into one of these categories: science, business, sports, technology. Respond with just the category name. Text: {text}"
try:
    result = provider.call_api(prompt, 50)
    print(f"Text: {text}")
    print(f"Category: {result}")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test entity extraction
print("Entity Extraction Test:")
print("-" * 30)
text = "John Smith and Mary Johnson attended the meeting in New York"
prompt = f"Extract all person names from this text. List them separated by commas. Text: {text}"
try:
    result = provider.call_api(prompt, 100)
    print(f"Text: {text}")
    print(f"People: {result}")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test math problem
print("Math Problem Test:")
print("-" * 30)
problem = "If John has 15 apples and gives away 7, how many does he have left?"
prompt = f"Solve this math problem and give just the numerical answer: {problem}"
try:
    result = provider.call_api(prompt, 50)
    print(f"Problem: {problem}")
    print(f"Answer: {result}")
except Exception as e:
    print(f"Error: {e}")

# Restore original keys
os.environ['ANTHROPIC_API_KEY'] = anthropic_key
os.environ['OPENAI_API_KEY'] = openai_key

print("\n" + "=" * 50)
print("Gemini Integration Test Complete!")