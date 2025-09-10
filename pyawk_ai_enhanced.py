#!/usr/bin/env python3
"""
PyAwk - A functional equivalent of awk written in Python
Supports most core awk functionality including pattern matching, field processing, and built-in variables.
Enhanced with real AI provider support.
"""

import sys
import re
import argparse
import math
import os
import json
import urllib.request
import urllib.parse
import time
from typing import List, Dict, Any, Callable, Optional, Union
from pathlib import Path

# Import AI providers
try:
    from ai_providers import get_ai_provider, reset_provider
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    def get_ai_provider():
        return None
    def reset_provider():
        pass


class AwkVariables:
    """Container for awk built-in variables"""
    def __init__(self):
        self.NR = 0      # Number of records (lines) processed
        self.FNR = 0     # File number of records (resets for each file)
        self.NF = 0      # Number of fields in current record
        self.FILENAME = ""  # Current filename
        self.FS = " "    # Field separator (regex pattern)
        self.OFS = " "   # Output field separator
        self.ORS = "\n"  # Output record separator
        self.RS = "\n"   # Record separator
        self.RSTART = 0  # Start of match for match() function
        self.RLENGTH = 0 # Length of match for match() function
        self.SUBSEP = "\034"  # Subscript separator for arrays
        
    def to_dict(self):
        """Return variables as dictionary for eval context"""
        return {
            'NR': self.NR,
            'FNR': self.FNR, 
            'NF': self.NF,
            'FILENAME': self.FILENAME,
            'FS': self.FS,
            'OFS': self.OFS,
            'ORS': self.ORS,
            'RS': self.RS,
            'RSTART': self.RSTART,
            'RLENGTH': self.RLENGTH,
            'SUBSEP': self.SUBSEP
        }


class AwkFunctions:
    """Awk built-in functions with AI enhancements"""
    
    @staticmethod
    def ai_call(prompt, max_tokens=100):
        """Call AI with a prompt - supports multiple providers!"""
        # Try to use real AI provider first
        if AI_AVAILABLE:
            try:
                provider = get_ai_provider()
                if provider:
                    response = provider.call_api(prompt, max_tokens)
                    if response is not None:
                        return response
            except Exception:
                pass  # Fall back to simulation
            
        # Fall back to simulation if no API available
        from ai_providers import SimulatedProvider
        sim = SimulatedProvider()
        return sim.call_api(prompt, max_tokens)
    
    @staticmethod
    def ai_sentiment(text):
        """Analyze sentiment of text using AI"""
        prompt = f"Analyze the sentiment of this text and respond with just one word: positive, negative, or neutral. Text: {text}"
        return AwkFunctions.ai_call(prompt, 50).lower()
    
    @staticmethod
    def ai_extract_info(text, info_type):
        """Extract specific information from text using AI"""
        prompt = f"Extract {info_type} from this text. If not found, return 'none'. Text: {text}"
        return AwkFunctions.ai_call(prompt, 100)
    
    @staticmethod
    def ai_classify(text, categories):
        """Classify text into one of the given categories"""
        cat_list = categories if isinstance(categories, str) else ", ".join(categories)
        prompt = f"Classify this text into one of these categories: {cat_list}. Respond with just the category name. Text: {text}"
        return AwkFunctions.ai_call(prompt, 50)
    
    @staticmethod
    def ai_translate(text, target_lang="Spanish"):
        """Translate text to target language"""
        prompt = f"Translate this text to {target_lang}. Respond with just the translation: {text}"
        return AwkFunctions.ai_call(prompt, 200)
    
    @staticmethod
    def ai_summarize(text, max_words=20):
        """Summarize text in max_words or less"""
        prompt = f"Summarize this text in {max_words} words or less: {text}"
        return AwkFunctions.ai_call(prompt, max_words * 2)
    
    @staticmethod
    def ai_generate(template, *args):
        """Generate text based on a template and variables"""
        prompt = f"Generate text based on this template: {template} with arguments: {args}"
        return AwkFunctions.ai_call(prompt, 200)
    
    @staticmethod
    def ai_math_word_problem(problem):
        """Solve math word problems using AI"""
        prompt = f"Solve this math problem and give just the numerical answer: {problem}"
        return AwkFunctions.ai_call(prompt, 100)
    
    @staticmethod
    def ai_entity_extract(text, entity_type="person"):
        """Extract entities (person, place, organization, etc.) from text"""
        prompt = f"Extract all {entity_type} entities from this text. List them separated by commas. Text: {text}"
        return AwkFunctions.ai_call(prompt, 150)
    
    @staticmethod
    def ai_fact_check(statement):
        """Basic fact checking using AI knowledge"""
        prompt = f"Is this statement likely true or false based on general knowledge? Respond with 'true', 'false', or 'uncertain': {statement}"
        result = AwkFunctions.ai_call(prompt, 50)
        return result.lower() if result else "uncertain"
    
    @staticmethod
    def length(s=""):
        """Return length of string"""
        return len(str(s))
    
    @staticmethod
    def substr(string, start, length=None):
        """Extract substring (1-indexed like awk)"""
        s = str(string)
        start = int(start) - 1  # Convert to 0-indexed
        if start < 0:
            start = 0
        if length is None:
            return s[start:]
        else:
            length = int(length)
            return s[start:start + length]
    
    @staticmethod
    def index(string, substring):
        """Find index of substring (1-indexed, 0 if not found)"""
        try:
            return str(string).index(str(substring)) + 1
        except ValueError:
            return 0
    
    @staticmethod
    def split(string, array_name, separator=" "):
        """Split string into array (returns number of elements)"""
        # This is simplified - in real awk this modifies a global array
        parts = re.split(separator, str(string))
        return len(parts)
    
    @staticmethod
    def gsub(pattern, replacement, target=""):
        """Global substitution (returns number of substitutions)"""
        result, count = re.subn(pattern, replacement, str(target))
        return count
    
    @staticmethod
    def sub(pattern, replacement, target=""):
        """Single substitution (returns number of substitutions)"""
        result, count = re.subn(pattern, replacement, str(target), count=1)
        return count
    
    @staticmethod
    def match(string, pattern):
        """Match pattern against string (returns position or 0)"""
        m = re.search(pattern, str(string))
        if m:
            return m.start() + 1  # 1-indexed
        return 0
    
    @staticmethod
    def tolower(string):
        """Convert to lowercase"""
        return str(string).lower()
    
    @staticmethod
    def toupper(string):
        """Convert to uppercase"""
        return str(string).upper()
    
    @staticmethod
    def sin(x):
        return math.sin(float(x))
    
    @staticmethod
    def cos(x):
        return math.cos(float(x))
    
    @staticmethod
    def atan2(y, x):
        return math.atan2(float(y), float(x))
    
    @staticmethod
    def exp(x):
        return math.exp(float(x))
    
    @staticmethod
    def log(x):
        return math.log(float(x))
    
    @staticmethod
    def sqrt(x):
        return math.sqrt(float(x))
    
    @staticmethod
    def int(x):
        return int(float(x))
    
    @staticmethod
    def rand():
        import random
        return random.random()
    
    @staticmethod
    def srand(seed=None):
        import random
        if seed is None:
            import time
            seed = int(time.time())
        random.seed(seed)
        return seed


class AwkProcessor:
    """Main awk processing engine"""
    
    def __init__(self, field_separator=" ", output_field_separator=" "):
        self.vars = AwkVariables()
        self.vars.FS = field_separator
        self.vars.OFS = output_field_separator
        self.fields = []  # $0, $1, $2, etc.
        self.user_vars = {}  # User-defined variables
        self.arrays = {}     # Associative arrays
        
        # Build function context
        self.functions = {}
        for name in dir(AwkFunctions):
            if not name.startswith('_'):
                self.functions[name] = getattr(AwkFunctions, name)
    
    def split_record(self, record):
        """Split record into fields based on FS"""
        if self.vars.FS == " ":
            # Default FS - split on runs of whitespace, strip leading/trailing
            fields = record.strip().split()
        elif self.vars.FS == "":
            # Empty FS - split into characters
            fields = list(record)
        else:
            # Use FS as regex pattern
            fields = re.split(self.vars.FS, record)
        
        # $0 is the whole record, $1, $2, ... are the fields
        self.fields = [record] + fields
        self.vars.NF = len(fields)
        return fields
    
    def get_field(self, n):
        """Get field $n (0-indexed internally but 1-indexed for user)"""
        if n == 0:
            return self.fields[0] if self.fields else ""
        elif 1 <= n < len(self.fields):
            return self.fields[n]
        else:
            return ""
    
    def set_field(self, n, value):
        """Set field $n"""
        value = str(value)
        # Extend fields array if necessary
        while len(self.fields) <= n:
            self.fields.append("")
        
        self.fields[n] = value
        
        # If setting a field > 0, rebuild $0
        if n > 0:
            self.fields[0] = self.vars.OFS.join(self.fields[1:])
            self.vars.NF = len(self.fields) - 1
    
    def build_context(self):
        """Build execution context for eval"""
        context = {}
        
        # Built-in variables
        context.update(self.vars.to_dict())
        
        # User variables
        context.update(self.user_vars)
        
        # Field access - create field variables $0, $1, $2, etc.
        for i in range(len(self.fields)):
            context[f'field_{i}'] = self.fields[i]
        
        # Functions
        context.update(self.functions)
        
        # Special functions for field access
        context['field'] = self.get_field
        context['set_field'] = self.set_field
        
        # Python built-ins we want to allow
        context.update({
            'print': print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            're': re,
            'abs': abs,
            'min': min,
            'max': max,
        })
        
        return context
    
    def evaluate_condition(self, condition, context):
        """Evaluate a condition (pattern)"""
        if condition is None or condition.strip() == "":
            return True
        
        try:
            # Handle regex patterns like /pattern/
            if condition.startswith('/') and condition.endswith('/'):
                pattern = condition[1:-1]  # Remove / /
                record = self.fields[0] if self.fields else ""
                return bool(re.search(pattern, record))
            
            # Convert awk operators to Python
            condition = condition.replace('&&', ' and ')
            condition = condition.replace('||', ' or ')
            condition = condition.replace('!', ' not ')
            
            # Handle field references like $1, $2
            condition = re.sub(r'\$(\d+)', r'field(\1)', condition)
            
            # Handle assignment to fields
            condition = re.sub(r'\$(\d+)\s*=\s*(.+)', r'set_field(\1, \2)', condition)
            
            result = eval(condition, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            print(f"Error evaluating condition '{condition}': {e}", file=sys.stderr)
            return False
    
    def execute_action(self, action, context):
        """Execute an action"""
        if not action or action.strip() == "":
            # Default action is print
            print(self.fields[0] if self.fields else "")
            return
        
        try:
            # Handle field references
            action = re.sub(r'\$(\d+)', r'field(\1)', action)
            
            # Handle assignment to fields
            action = re.sub(r'\$(\d+)\s*=\s*(.+)', r'set_field(\1, \2)', action)
            
            # Handle multiple statements separated by semicolons
            statements = [s.strip() for s in action.split(';') if s.strip()]
            
            for stmt in statements:
                # Handle awk-style print statements (convert to Python print)
                if stmt == "print":
                    print(self.fields[0] if self.fields else "")
                    continue
                elif stmt.startswith("print "):
                    # Convert "print expr1, expr2" to "print(expr1, expr2)"
                    print_args = stmt[6:].strip()  # Remove "print "
                    if print_args:
                        stmt = f"print({print_args})"
                    else:
                        print(self.fields[0] if self.fields else "")
                        continue
                
                # Execute statement
                exec(stmt, {"__builtins__": {"print": print}}, context)
                
                # Update user variables from context
                for key, value in context.items():
                    if (key not in self.vars.to_dict() and 
                        key not in self.functions and
                        not key.startswith('field') and
                        key not in ['print', 'len', 'str', 'int', 'float', 're', 'abs', 'min', 'max']):
                        self.user_vars[key] = value
                        
        except NameError as e:
            # Handle undefined variables by initializing them to 0
            var_name = str(e).split("'")[1]
            if var_name not in context:
                self.user_vars[var_name] = 0
                context[var_name] = 0
                # Retry the action
                self.execute_action(action, context)
        except Exception as e:
            print(f"Error executing action '{action}': {e}", file=sys.stderr)
    
    def process_file(self, filename, rules):
        """Process a single file with given rules"""
        if filename == "-":
            file_obj = sys.stdin
            self.vars.FILENAME = ""
        else:
            try:
                file_obj = open(filename, 'r')
                self.vars.FILENAME = filename
            except IOError as e:
                print(f"Error opening {filename}: {e}", file=sys.stderr)
                return
        
        self.vars.FNR = 0
        
        try:
            # Execute BEGIN rules
            context = self.build_context()
            for condition, action in rules:
                if condition == "BEGIN":
                    self.execute_action(action, context)
            
            # Process each line
            for line in file_obj:
                line = line.rstrip('\n\r')
                self.vars.NR += 1
                self.vars.FNR += 1
                
                self.split_record(line)
                context = self.build_context()
                
                # Execute pattern-action rules
                for condition, action in rules:
                    if condition not in ("BEGIN", "END"):
                        if self.evaluate_condition(condition, context):
                            self.execute_action(action, context)
                            # Update context in case variables changed
                            context = self.build_context()
            
            # Execute END rules
            context = self.build_context()
            for condition, action in rules:
                if condition == "END":
                    self.execute_action(action, context)
                    
        finally:
            if filename != "-":
                file_obj.close()


def parse_awk_program(program):
    """Parse awk program into rules"""
    rules = []
    
    # Simple parser - doesn't handle all awk syntax complexities
    # but covers the most common cases
    
    # Handle BEGIN and END blocks
    begin_pattern = r'BEGIN\s*\{([^}]*)\}'
    end_pattern = r'END\s*\{([^}]*)\}'
    
    for match in re.finditer(begin_pattern, program, re.DOTALL):
        rules.append(("BEGIN", match.group(1).strip()))
    
    for match in re.finditer(end_pattern, program, re.DOTALL):
        rules.append(("END", match.group(1).strip()))
    
    # Remove BEGIN and END blocks from program
    program = re.sub(begin_pattern, '', program, flags=re.DOTALL)
    program = re.sub(end_pattern, '', program, flags=re.DOTALL)
    
    # Parse remaining pattern-action rules
    # This is a simplified parser
    lines = program.split('\n')
    current_rule = ""
    brace_count = 0
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        current_rule += line + " "
        brace_count += line.count('{') - line.count('}')
        
        if brace_count == 0 and current_rule.strip():
            # Complete rule
            rule = current_rule.strip()
            
            if '{' in rule:
                # Pattern { action }
                parts = rule.split('{', 1)
                pattern = parts[0].strip()
                action = parts[1].rsplit('}', 1)[0].strip()
                rules.append((pattern if pattern else None, action))
            else:
                # Just a pattern (default action is print)
                rules.append((rule, ""))
            
            current_rule = ""
    
    return rules


def main():
    parser = argparse.ArgumentParser(
        description="PyAwk - A Python implementation of awk with AI enhancements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 'NR > 1' file.txt                    # Print lines after first
  %(prog)s '{print $2}' file.txt                # Print second field
  %(prog)s -F: '{print $1}' /etc/passwd         # Use : as field separator
  %(prog)s 'BEGIN {print "Header"} {print NR, $0}' file.txt
  %(prog)s '/pattern/ {print "Found:", $0}' file.txt
  
AI Examples:
  %(prog)s '{sentiment = ai_sentiment($0); print $0, "->", sentiment}' posts.txt
  %(prog)s '{category = ai_classify($0, "urgent,normal,low"); print category ":", $0}' tickets.txt
        """
    )
    
    parser.add_argument('program', help='AWK program to execute')
    parser.add_argument('files', nargs='*', default=['-'], 
                       help='Input files (default: stdin)')
    parser.add_argument('-F', '--field-separator', default=' ',
                       help='Field separator (default: space)')
    parser.add_argument('-v', '--assign', action='append', default=[],
                       help='Variable assignment (var=value)')
    parser.add_argument('--version', action='version', version='PyAwk 1.1 with AI')
    
    args = parser.parse_args()
    
    # Parse variable assignments
    user_vars = {}
    for assignment in args.assign:
        if '=' in assignment:
            var, val = assignment.split('=', 1)
            # Try to convert to number if possible
            try:
                val = int(val)
            except ValueError:
                try:
                    val = float(val)
                except ValueError:
                    pass  # Keep as string
            user_vars[var] = val
    
    # Parse the awk program
    rules = parse_awk_program(args.program)
    
    # Create processor
    processor = AwkProcessor(field_separator=args.field_separator)
    processor.user_vars.update(user_vars)
    
    # Process files
    for filename in args.files:
        processor.process_file(filename, rules)


if __name__ == "__main__":
    main()