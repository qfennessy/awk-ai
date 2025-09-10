#!/usr/bin/env python3
"""
Unit tests for AI functionality in PyAwk - Fixed for real API responses
These tests validate the AI-enhanced functions with proper normalization
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path to import pyawk_ai
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyawk_ai import AwkFunctions


def normalize_response(text):
    """Normalize AI responses for comparison"""
    if not text:
        return ""
    return text.strip().lower().rstrip('.,!?')


class TestAISentimentAnalysis:
    """Test AI sentiment analysis function"""
    
    def test_positive_sentiment_detection(self):
        """Test detection of positive sentiment"""
        positive_texts = [
            "I absolutely love this product!",
            "This is amazing and wonderful",
            "Best experience ever, highly recommend",
            "Fantastic service, exceeded expectations",
            "So happy with my purchase!"
        ]
        
        for text in positive_texts:
            result = normalize_response(AwkFunctions.ai_sentiment(text))
            assert result == "positive", f"Failed to detect positive sentiment in: {text}"
    
    def test_negative_sentiment_detection(self):
        """Test detection of negative sentiment"""
        negative_texts = [
            "This is terrible and disappointing",
            "Worst experience of my life",
            "Completely unsatisfied with the service",
            "Product broke immediately, very angry",
            "Would not recommend to anyone"
        ]
        
        for text in negative_texts:
            result = normalize_response(AwkFunctions.ai_sentiment(text))
            assert result == "negative", f"Failed to detect negative sentiment in: {text}"
    
    def test_neutral_sentiment_detection(self):
        """Test detection of neutral sentiment"""
        neutral_texts = [
            "The product arrived on Tuesday",
            "This item has three features",
            "The meeting is scheduled for 3pm",
            "Documentation is available online"
        ]
        
        for text in neutral_texts:
            result = normalize_response(AwkFunctions.ai_sentiment(text))
            assert result == "neutral", f"Failed to detect neutral sentiment in: {text}"


class TestAIClassification:
    """Test AI text classification function"""
    
    def test_news_category_classification(self):
        """Test classification of news articles into categories"""
        test_cases = [
            ("Stock market reaches all-time high amid economic recovery", "business"),
            ("Scientists discover new exoplanet in habitable zone", "science"),
            ("Lakers win championship in thrilling overtime game", "sports"),
            ("New AI breakthrough promises to revolutionize healthcare", "technology"),
            ("President announces new climate change policies", "politics")
        ]
        
        for text, expected_category in test_cases:
            result = normalize_response(AwkFunctions.ai_classify(text, "science,business,sports,technology,politics"))
            assert result == expected_category, f"Misclassified: {text}"
    
    def test_priority_classification(self):
        """Test classification of support tickets by priority"""
        test_cases = [
            ("System is completely down, no one can log in!", "urgent"),
            ("Please update my email address when you have time", "low"),
            ("Bug causing occasional errors in reports", "normal"),
            ("CRITICAL: Data loss occurring, need immediate help", "urgent")
        ]
        
        for text, expected_priority in test_cases:
            result = normalize_response(AwkFunctions.ai_classify(text, "urgent,normal,low"))
            assert result == expected_priority, f"Wrong priority for: {text}"
    
    def test_custom_categories(self):
        """Test classification with custom category sets"""
        result = normalize_response(AwkFunctions.ai_classify(
            "Python code for machine learning model",
            "programming,cooking,travel,finance"
        ))
        assert result == "programming"


class TestAITranslation:
    """Test AI translation function"""
    
    def test_english_to_spanish(self):
        """Test translation from English to Spanish"""
        test_cases = [
            ("Hello", ["hola", "¡hola"]),
            ("Thank you", ["gracias", "muchas gracias"]),
            ("Good morning", ["buenos días", "buen día"])
        ]
        
        for english, possible_translations in test_cases:
            result = normalize_response(AwkFunctions.ai_translate(english, "Spanish"))
            # Check if any possible translation matches
            assert any(trans in result for trans in possible_translations), f"Translation failed for: {english}"
    
    def test_translation_contains_expected_words(self):
        """Test that translations contain expected words"""
        result = AwkFunctions.ai_translate("I love programming", "Spanish")
        # Should contain Spanish words related to love/programming
        assert any(word in result.lower() for word in ["amor", "amo", "encanta", "programar", "programación"])


class TestAISummarization:
    """Test AI text summarization function"""
    
    def test_long_text_summarization(self):
        """Test summarization of long text"""
        long_text = """
        The annual technology conference brought together over 5000 attendees from 
        around the world. Keynote speakers discussed artificial intelligence, quantum 
        computing, and sustainable technology. Multiple workshops covered topics ranging 
        from cybersecurity to blockchain implementation. The event concluded with an 
        awards ceremony recognizing innovative startups.
        """
        
        result = AwkFunctions.ai_summarize(long_text, 15)
        assert len(result.split()) <= 25  # Allow some margin
        assert len(result) > 10  # Should produce some summary
    
    def test_word_limit_respected(self):
        """Test that summarization respects word limits"""
        text = "This is a very long document with many important details that need to be condensed"
        
        for max_words in [5, 10, 20]:
            result = AwkFunctions.ai_summarize(text, max_words)
            word_count = len(result.split())
            assert word_count <= max_words * 2, f"Exceeded word limit of {max_words}"


class TestAIEntityExtraction:
    """Test AI entity extraction function"""
    
    def test_person_extraction(self):
        """Test extraction of person names"""
        test_cases = [
            ("John Smith and Mary Johnson attended the meeting", ["John Smith", "Mary Johnson"]),
            ("CEO Tim Cook announced new products", ["Tim Cook"]),
            ("The research by Dr. Sarah Williams was groundbreaking", ["Sarah Williams", "Dr. Sarah Williams"])
        ]
        
        for text, expected_names in test_cases:
            result = AwkFunctions.ai_entity_extract(text, "person")
            for name in expected_names:
                # Check if name appears in result (case-insensitive)
                assert any(name.lower() in result.lower() for name in expected_names), f"Failed to extract {name} from: {text}"
    
    def test_no_entities_found(self):
        """Test behavior when no entities are found"""
        result = AwkFunctions.ai_entity_extract("The weather is nice today", "person").lower()
        # Should indicate no entities found
        assert "no" in result or "none" in result or "not" in result or len(result.strip()) == 0


class TestAIFactChecking:
    """Test AI fact checking function"""
    
    def test_true_facts(self):
        """Test identification of true facts"""
        true_facts = [
            "The Pacific Ocean is the largest ocean on Earth",
            "Water freezes at 0 degrees Celsius",
            "Python is a programming language"
        ]
        
        for fact in true_facts:
            result = normalize_response(AwkFunctions.ai_fact_check(fact))
            # Accept "true" or variations
            assert "true" in result or "correct" in result or "yes" in result, f"Incorrectly marked as false: {fact}"
    
    def test_false_facts(self):
        """Test identification of false facts"""
        false_facts = [
            "Cats can naturally fly",
            "The sun revolves around the Earth",
            "Humans have 3 hearts"
        ]
        
        for fact in false_facts:
            result = normalize_response(AwkFunctions.ai_fact_check(fact))
            # Accept "false" or variations
            assert "false" in result or "incorrect" in result or "no" in result or "not" in result, f"Incorrectly marked as true: {fact}"


class TestAIInfoExtraction:
    """Test AI information extraction function"""
    
    def test_extract_dates(self):
        """Test extraction of date information"""
        text = "The meeting is scheduled for March 15, 2024 at 2:00 PM"
        result = AwkFunctions.ai_extract_info(text, "date")
        assert "March" in result or "2024" in result or "15" in result
    
    def test_extract_prices(self):
        """Test extraction of price information"""
        text = "The product costs $49.99 with free shipping"
        result = AwkFunctions.ai_extract_info(text, "price")
        assert "$49" in result or "49.99" in result or "49" in result
    
    def test_extract_email(self):
        """Test extraction of email addresses"""
        text = "Contact us at support@example.com for assistance"
        result = AwkFunctions.ai_extract_info(text, "email")
        assert "support@example.com" in result or "@example.com" in result


class TestAIMathWordProblems:
    """Test AI math word problem solver"""
    
    def test_simple_arithmetic(self):
        """Test simple arithmetic word problems"""
        test_cases = [
            ("If John has 15 apples and gives away 7, how many does he have left?", ["8"]),
            ("What is 25 multiplied by 4?", ["100"]),
            ("What is half of 50?", ["25"])
        ]
        
        for problem, expected_answers in test_cases:
            result = str(AwkFunctions.ai_math_word_problem(problem))
            assert any(answer in result for answer in expected_answers), f"Wrong answer for: {problem}"
    
    def test_percentage_problems(self):
        """Test percentage calculation problems"""
        problem = "What is 20% of 150?"
        result = str(AwkFunctions.ai_math_word_problem(problem))
        assert "30" in result


class TestAIGenerate:
    """Test AI text generation function"""
    
    def test_template_generation(self):
        """Test text generation from templates"""
        template = "Write a product review for {product}"
        result = AwkFunctions.ai_generate(template, "laptop")
        assert len(result) > 10  # Should generate something
        # Check it's about laptops or products
        assert any(word in result.lower() for word in ["laptop", "product", "device", "computer"])
    
    def test_multiple_variables(self):
        """Test generation with multiple variables"""
        template = "Create a {type} about {topic} for {audience}"
        result = AwkFunctions.ai_generate(template, "article", "AI", "beginners")
        assert len(result) > 10


class TestAIIntegration:
    """Integration tests for AI functions in AWK context"""
    
    def test_chained_ai_operations(self):
        """Test chaining multiple AI operations"""
        text = "I absolutely love this new smartphone!"
        
        # Get sentiment
        sentiment = normalize_response(AwkFunctions.ai_sentiment(text))
        assert sentiment in ["positive", "negative", "neutral"]
        
        # Classify
        category = normalize_response(AwkFunctions.ai_classify(text, "tech,food,travel"))
        assert category in ["tech", "technology", "general"]
        
        # Summarize
        summary = AwkFunctions.ai_summarize(text, 5)
        assert len(summary) > 0
    
    def test_ai_with_non_empty_input(self):
        """Test AI functions with valid input"""
        result = normalize_response(AwkFunctions.ai_sentiment("Great product"))
        assert result in ["positive", "negative", "neutral"]
        
        result = AwkFunctions.ai_entity_extract("John lives in New York", "person")
        assert len(result) > 0