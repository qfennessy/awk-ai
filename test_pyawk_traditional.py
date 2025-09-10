#!/usr/bin/env python3
"""
Unit tests for traditional AWK functionality in PyAwk
Tests core AWK functions, field processing, and built-in variables
"""

import pytest
import math
import sys
import os
from io import StringIO
from unittest.mock import patch

# Add parent directory to path to import pyawk_ai
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyawk_ai import AwkFunctions, AwkProcessor, AwkVariables, parse_awk_program


class TestAwkStringFunctions:
    """Test traditional AWK string functions"""
    
    def test_length_function(self):
        """Test the length() function"""
        assert AwkFunctions.length("hello") == 5
        assert AwkFunctions.length("") == 0
        assert AwkFunctions.length("test string") == 11
        assert AwkFunctions.length(123) == 3  # Should convert to string
        assert AwkFunctions.length(None) == 4  # "None" as string
    
    def test_substr_function(self):
        """Test the substr() function (1-indexed)"""
        assert AwkFunctions.substr("hello", 1, 3) == "hel"
        assert AwkFunctions.substr("hello", 2, 2) == "el"
        assert AwkFunctions.substr("hello", 3) == "llo"  # No length = rest of string
        assert AwkFunctions.substr("hello", 6) == ""  # Start beyond string
        assert AwkFunctions.substr("hello", 0, 2) == "he"  # 0 treated as 1
    
    def test_index_function(self):
        """Test the index() function (1-indexed, 0 if not found)"""
        assert AwkFunctions.index("hello world", "world") == 7
        assert AwkFunctions.index("hello", "ll") == 3
        assert AwkFunctions.index("hello", "xyz") == 0  # Not found
        assert AwkFunctions.index("", "test") == 0  # Empty string
        assert AwkFunctions.index("test", "") == 1  # Empty substring
    
    def test_toupper_function(self):
        """Test the toupper() function"""
        assert AwkFunctions.toupper("hello") == "HELLO"
        assert AwkFunctions.toupper("Hello World") == "HELLO WORLD"
        assert AwkFunctions.toupper("123abc") == "123ABC"
        assert AwkFunctions.toupper("") == ""
    
    def test_tolower_function(self):
        """Test the tolower() function"""
        assert AwkFunctions.tolower("HELLO") == "hello"
        assert AwkFunctions.tolower("Hello World") == "hello world"
        assert AwkFunctions.tolower("123ABC") == "123abc"
        assert AwkFunctions.tolower("") == ""
    
    def test_match_function(self):
        """Test the match() function with regex patterns"""
        assert AwkFunctions.match("hello world", "world") == 7
        assert AwkFunctions.match("test123", r"\d+") == 5  # First digit at position 5
        assert AwkFunctions.match("hello", "xyz") == 0  # Not found
        assert AwkFunctions.match("abc def", r"\s") == 4  # Space at position 4


class TestAwkMathFunctions:
    """Test AWK mathematical functions"""
    
    def test_sin_function(self):
        """Test the sin() function"""
        assert abs(AwkFunctions.sin(0)) < 0.0001
        assert abs(AwkFunctions.sin(math.pi/2) - 1) < 0.0001
        assert abs(AwkFunctions.sin(math.pi)) < 0.0001
    
    def test_cos_function(self):
        """Test the cos() function"""
        assert abs(AwkFunctions.cos(0) - 1) < 0.0001
        assert abs(AwkFunctions.cos(math.pi/2)) < 0.0001
        assert abs(AwkFunctions.cos(math.pi) + 1) < 0.0001
    
    def test_sqrt_function(self):
        """Test the sqrt() function"""
        assert AwkFunctions.sqrt(4) == 2.0
        assert AwkFunctions.sqrt(9) == 3.0
        assert abs(AwkFunctions.sqrt(2) - 1.4142135) < 0.0001
        assert AwkFunctions.sqrt(0) == 0.0
    
    def test_exp_log_functions(self):
        """Test exp() and log() functions"""
        assert abs(AwkFunctions.exp(0) - 1) < 0.0001
        assert abs(AwkFunctions.exp(1) - math.e) < 0.0001
        assert abs(AwkFunctions.log(math.e) - 1) < 0.0001
        assert abs(AwkFunctions.log(10) - 2.302585) < 0.0001
    
    def test_int_function(self):
        """Test the int() function"""
        assert AwkFunctions.int(3.7) == 3
        assert AwkFunctions.int(3.2) == 3
        assert AwkFunctions.int(-2.8) == -2
        assert AwkFunctions.int("5.9") == 5
    
    def test_atan2_function(self):
        """Test the atan2() function"""
        assert abs(AwkFunctions.atan2(1, 1) - math.pi/4) < 0.0001
        assert abs(AwkFunctions.atan2(0, 1)) < 0.0001
        assert abs(AwkFunctions.atan2(1, 0) - math.pi/2) < 0.0001


class TestAwkVariables:
    """Test AWK built-in variables"""
    
    def test_initial_values(self):
        """Test initial values of AWK variables"""
        vars = AwkVariables()
        assert vars.NR == 0
        assert vars.FNR == 0
        assert vars.NF == 0
        assert vars.FILENAME == ""
        assert vars.FS == " "
        assert vars.OFS == " "
        assert vars.ORS == "\n"
        assert vars.RS == "\n"
    
    def test_to_dict_method(self):
        """Test conversion to dictionary for eval context"""
        vars = AwkVariables()
        vars.NR = 5
        vars.NF = 3
        vars.FILENAME = "test.txt"
        
        d = vars.to_dict()
        assert d['NR'] == 5
        assert d['NF'] == 3
        assert d['FILENAME'] == "test.txt"
        assert d['FS'] == " "


class TestAwkProcessor:
    """Test AWK processor functionality"""
    
    def test_field_splitting_default(self):
        """Test field splitting with default separator (space)"""
        processor = AwkProcessor()
        processor.split_record("one two three")
        
        assert processor.get_field(0) == "one two three"
        assert processor.get_field(1) == "one"
        assert processor.get_field(2) == "two"
        assert processor.get_field(3) == "three"
        assert processor.get_field(4) == ""  # Beyond fields
        assert processor.vars.NF == 3
    
    def test_field_splitting_custom_separator(self):
        """Test field splitting with custom separator"""
        processor = AwkProcessor(field_separator=",")
        processor.split_record("apple,banana,cherry")
        
        assert processor.get_field(0) == "apple,banana,cherry"
        assert processor.get_field(1) == "apple"
        assert processor.get_field(2) == "banana"
        assert processor.get_field(3) == "cherry"
        assert processor.vars.NF == 3
    
    def test_field_splitting_regex_separator(self):
        """Test field splitting with regex separator"""
        processor = AwkProcessor(field_separator=r"\s+")
        processor.split_record("one    two  three")
        
        assert processor.get_field(1) == "one"
        assert processor.get_field(2) == "two"
        assert processor.get_field(3) == "three"
        assert processor.vars.NF == 3
    
    def test_set_field(self):
        """Test setting field values"""
        processor = AwkProcessor()
        processor.split_record("one two three")
        
        processor.set_field(2, "TWO")
        assert processor.get_field(2) == "TWO"
        assert processor.get_field(0) == "one TWO three"  # $0 rebuilt
        
        processor.set_field(5, "five")  # Beyond current fields
        assert processor.get_field(5) == "five"
        assert processor.vars.NF == 5
    
    def test_evaluate_regex_pattern(self):
        """Test regex pattern evaluation"""
        processor = AwkProcessor()
        processor.split_record("hello world")
        context = processor.build_context()
        
        assert processor.evaluate_condition("/world/", context) == True
        assert processor.evaluate_condition("/xyz/", context) == False
        assert processor.evaluate_condition("/^hello/", context) == True
        assert processor.evaluate_condition("/world$/", context) == True


class TestAwkProgramParsing:
    """Test AWK program parsing"""
    
    def test_parse_simple_action(self):
        """Test parsing simple action without pattern"""
        rules = parse_awk_program('{print}')
        assert len(rules) == 1
        assert rules[0] == (None, 'print')
    
    def test_parse_pattern_action(self):
        """Test parsing pattern with action"""
        rules = parse_awk_program('/test/ {print "found"}')
        assert len(rules) == 1
        assert rules[0] == ('/test/', 'print "found"')
    
    def test_parse_begin_end_blocks(self):
        """Test parsing BEGIN and END blocks"""
        program = 'BEGIN {print "start"} {print} END {print "end"}'
        rules = parse_awk_program(program)
        
        assert ('BEGIN', 'print "start"') in rules
        assert ('END', 'print "end"') in rules
        assert (None, 'print') in rules
    
    def test_parse_multiple_rules(self):
        """Test parsing multiple pattern-action rules"""
        program = '''
        NR == 1 {print "first"}
        NR > 5 {print "after 5"}
        /error/ {print "error found"}
        '''
        rules = parse_awk_program(program)
        assert len(rules) == 3


class TestAwkIntegration:
    """Integration tests for complete AWK processing"""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_basic_print(self, mock_stdout):
        """Test basic print functionality"""
        processor = AwkProcessor()
        rules = parse_awk_program('{print field(0)}')
        
        # Simulate processing a line
        processor.split_record("test line")
        context = processor.build_context()
        processor.execute_action('print field(0)', context)
        
        assert mock_stdout.getvalue() == "test line\n"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_field_printing(self, mock_stdout):
        """Test printing specific fields"""
        processor = AwkProcessor()
        processor.split_record("one two three")
        context = processor.build_context()
        
        processor.execute_action('print field(2)', context)
        assert "two" in mock_stdout.getvalue()
    
    def test_nr_increment(self):
        """Test NR (record number) increment"""
        processor = AwkProcessor()
        assert processor.vars.NR == 0
        
        # Simulate processing lines with a simple stdin mock
        with patch('builtins.open', return_value=StringIO("line1\nline2\nline3\n")):
            processor.process_file("test.txt", [(None, "")])
        
        assert processor.vars.NR == 3