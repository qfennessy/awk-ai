#!/usr/bin/env python3
"""Test script to verify AI integration with real API"""

import sys
sys.path.insert(0, '.')

from ai_providers import get_ai_provider, reset_provider

# Test direct AI provider
print("Testing AI Provider Integration...")
print("=" * 50)

provider = get_ai_provider()
print(f"Active provider: {provider.__class__.__name__}")

# Test sentiment analysis
test_texts = [
    "I absolutely love this product!",
    "This is terrible and disappointing",
    "The weather is cloudy today"
]

print("\nSentiment Analysis Tests:")
print("-" * 30)
for text in test_texts:
    prompt = f"Analyze the sentiment of this text and respond with just one word: positive, negative, or neutral. Text: {text}"
    result = provider.call_api(prompt, 50)
    print(f"Text: {text[:30]}...")
    print(f"Result: {result}")
    print()

# Test classification
print("Classification Test:")
print("-" * 30)
text = "Scientists discover new species in the ocean"
prompt = f"Classify this text into one of these categories: science, business, sports, technology. Respond with just the category name. Text: {text}"
result = provider.call_api(prompt, 50)
print(f"Text: {text}")
print(f"Category: {result}")
print()

# Test entity extraction
print("Entity Extraction Test:")
print("-" * 30)
text = "John Smith and Mary Johnson attended the meeting in New York"
prompt = f"Extract all person names from this text. List them separated by commas. Text: {text}"
result = provider.call_api(prompt, 100)
print(f"Text: {text}")
print(f"People: {result}")
print()

# Test math problem
print("Math Problem Test:")
print("-" * 30)
problem = "If John has 15 apples and gives away 7, how many does he have left?"
prompt = f"Solve this math problem and give just the numerical answer: {problem}"
result = provider.call_api(prompt, 50)
print(f"Problem: {problem}")
print(f"Answer: {result}")

print("\n" + "=" * 50)
print("AI Integration Test Complete!")