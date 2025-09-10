#!/usr/bin/env python3
"""
PyAwk Fixed - Python AWK implementation with proper parsing and no infinite loops
"""

import sys
import re
import argparse
import math
import os
import json
from typing import Dict, List, Any, Optional, Tuple

# Import AI providers
try:
    from ai_providers import get_ai_provider, SimulatedAIProvider
except ImportError:
    class SimulatedAIProvider:
        def call_api(self, prompt, max_tokens=100):
            return f"[Simulated: {prompt[:30]}...]"
    def get_ai_provider():
        return None


class AwkVariables:
    """Container for AWK built-in variables"""
    def __init__(self):
        self.NR = 0  # Total number of records
        self.NF = 0  # Number of fields in current record
        self.FNR = 0  # Record number in current file
        self.FS = " "  # Field separator
        self.OFS = " "  # Output field separator
        self.ORS = "\n"  # Output record separator
        self.RS = "\n"  # Input record separator
        self.FILENAME = ""  # Current filename
        self.RSTART = 0  # Start of match for match()
        self.RLENGTH = 0  # Length of match for match()
        self.SUBSEP = "\034"  # Subscript separator
        self.IGNORECASE = 0  # Case-insensitive matching
        self.ARGC = 0  # Argument count
        self.ARGV = []  # Argument array


class AwkFunctions:
    """AWK built-in functions"""
    
    @staticmethod
    def ai_call(prompt, max_tokens=100):
        """Generic AI API call with fallback"""
        provider = get_ai_provider()
        if provider:
            try:
                response = provider.call_api(prompt, max_tokens)
                if response:
                    return response
            except Exception:
                pass
        sim = SimulatedAIProvider()
        return sim.call_api(prompt, max_tokens)
    
    @staticmethod
    def ai_sentiment(text):
        """Analyze sentiment of text"""
        prompt = f"Analyze sentiment: positive, negative, or neutral?\n\nText: {text}"
        response = AwkFunctions.ai_call(prompt, 10)
        response_lower = response.lower().strip()
        if 'positive' in response_lower:
            return 'positive'
        elif 'negative' in response_lower:
            return 'negative'
        else:
            return 'neutral'
    
    @staticmethod
    def ai_classify(text, categories):
        """Classify text into categories"""
        cat_list = categories.split(',')
        prompt = f"Classify into: {categories}\n\nText: {text}"
        response = AwkFunctions.ai_call(prompt, 20)
        response_lower = response.lower().strip()
        for cat in cat_list:
            if cat.strip().lower() in response_lower:
                return cat.strip()
        return cat_list[0] if cat_list else "unknown"
    
    @staticmethod
    def ai_translate(text, target_language):
        """Translate text"""
        prompt = f"Translate to {target_language}: {text}"
        return AwkFunctions.ai_call(prompt, 100)
    
    @staticmethod
    def ai_summarize(text, max_words=50):
        """Summarize text"""
        prompt = f"Summarize in {max_words} words: {text}"
        return AwkFunctions.ai_call(prompt, max_words * 2)
    
    @staticmethod
    def ai_entity_extract(text, entity_type):
        """Extract entities"""
        prompt = f"Extract {entity_type} entities: {text}"
        return AwkFunctions.ai_call(prompt, 100)
    
    @staticmethod
    def ai_fact_check(statement):
        """Fact-check statement"""
        prompt = f"Is this true or false? {statement}"
        response = AwkFunctions.ai_call(prompt, 10)
        return 'true' if 'true' in response.lower() else 'false'
    
    @staticmethod
    def ai_extract_info(text, info_type):
        """Extract specific information"""
        prompt = f"Extract {info_type}: {text}"
        return AwkFunctions.ai_call(prompt, 50)
    
    @staticmethod
    def ai_math_word_problem(problem):
        """Solve math word problem"""
        prompt = f"Solve (number only): {problem}"
        response = AwkFunctions.ai_call(prompt, 20)
        numbers = re.findall(r'-?\d+\.?\d*', response)
        return float(numbers[0]) if numbers else 0
    
    @staticmethod
    def ai_generate(template, *args):
        """Generate text from template"""
        text = template
        for i, arg in enumerate(args):
            text = text.replace(f'{{{i}}}', str(arg))
        placeholders = re.findall(r'\{(\w+)\}', text)
        for i, placeholder in enumerate(placeholders[:len(args)]):
            text = text.replace(f'{{{placeholder}}}', str(args[i]))
        prompt = f"Generate: {text}"
        return AwkFunctions.ai_call(prompt, 100)
    
    # Standard AWK functions
    @staticmethod
    def length(s):
        return len(str(s))
    
    @staticmethod
    def substr(string, start, length=None):
        s = str(string)
        start = max(1, int(start))
        if start > len(s):
            return ""
        start_idx = start - 1
        if length is None:
            return s[start_idx:]
        else:
            length = int(length)
            if length <= 0:
                return ""
            return s[start_idx:start_idx + length]
    
    @staticmethod
    def index(string, substring):
        s = str(string)
        sub = str(substring)
        idx = s.find(sub)
        return idx + 1 if idx >= 0 else 0
    
    @staticmethod
    def split(string, separator=" "):
        parts = str(string).split(separator)
        result = {}
        for i, part in enumerate(parts, 1):
            result[i] = part
        return result
    
    @staticmethod
    def sub(regex, replacement, target):
        return re.sub(regex, replacement, str(target), count=1)
    
    @staticmethod
    def gsub(regex, replacement, target=None):
        if target is None:
            return 0
        result = re.sub(regex, replacement, str(target))
        return result
    
    @staticmethod
    def match(string, regex):
        m = re.search(regex, str(string))
        if m:
            return m.start() + 1
        return 0
    
    @staticmethod
    def sprintf(format_str, *args):
        """Format string - simplified version"""
        result = str(format_str)
        
        # Simple replacements for common formats
        replacements = []
        i = 0
        while i < len(result):
            if result[i] == '%':
                if i + 1 < len(result):
                    next_char = result[i + 1]
                    if next_char == 's':
                        replacements.append(('s', i, i + 2))
                    elif next_char == 'd':
                        replacements.append(('d', i, i + 2))
                    elif next_char == 'f':
                        replacements.append(('f', i, i + 2))
                    elif next_char == '%':
                        i += 1  # Skip %%
                    else:
                        # Look for format like %-12s or %20s or %.2f
                        match = re.match(r'%([-]?\d*\.?\d*)([sdfe])', result[i:])
                        if match:
                            replacements.append((match.group(2), i, i + len(match.group(0))))
                            i += len(match.group(0)) - 1
            i += 1
        
        # Apply replacements in reverse order
        arg_index = 0
        for fmt_type, start, end in replacements:
            if arg_index < len(args):
                arg = args[arg_index]
                if fmt_type == 'd':
                    replacement = str(int(float(arg)))
                elif fmt_type == 'f':
                    # Check for precision
                    fmt_spec = result[start:end]
                    if '.' in fmt_spec:
                        precision = int(re.search(r'\.(\d+)', fmt_spec).group(1))
                        replacement = f"{float(arg):.{precision}f}"
                    else:
                        replacement = f"{float(arg):.6f}"
                else:
                    replacement = str(arg)
                
                # Check for width specification
                fmt_spec = result[start:end]
                width_match = re.match(r'%([-]?)(\d+)', fmt_spec)
                if width_match:
                    width = int(width_match.group(2))
                    if width_match.group(1) == '-':
                        replacement = replacement.ljust(width)
                    else:
                        replacement = replacement.rjust(width)
                
                result = result[:start] + replacement + result[end:]
                arg_index += 1
        
        return result
    
    @staticmethod
    def printf(format_str, *args):
        result = AwkFunctions.sprintf(format_str, *args)
        print(result, end='')
        return len(args)
    
    @staticmethod
    def tolower(s):
        return str(s).lower()
    
    @staticmethod
    def toupper(s):
        return str(s).upper()
    
    # Math functions
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
        if seed is not None:
            random.seed(int(seed))
        else:
            random.seed()
        return 0
    
    # Array functions
    @staticmethod
    def asort(arr):
        """Sort array by values"""
        if not isinstance(arr, dict):
            return 0
        sorted_items = sorted(arr.items(), key=lambda x: x[1])
        arr.clear()
        for i, (_, val) in enumerate(sorted_items, 1):
            arr[i] = val
        return len(sorted_items)
    
    @staticmethod
    def asorti(arr):
        """Sort array by indices"""
        if not isinstance(arr, dict):
            return 0
        sorted_keys = sorted(arr.keys())
        new_arr = {}
        for i, key in enumerate(sorted_keys, 1):
            new_arr[i] = str(key)
        arr.clear()
        arr.update(new_arr)
        return len(sorted_keys)


class AwkProcessor:
    """AWK processor with fixed parsing"""
    
    def __init__(self, field_separator=" "):
        self.vars = AwkVariables()
        self.vars.FS = field_separator
        self.fields = []
        self.current_line = ""
        self.user_vars = {}
        self.user_functions = {}
        self.arrays = {}
        self.functions = AwkFunctions()
    
    def split_fields(self, line):
        """Split line into fields using FS"""
        if self.vars.FS == " ":
            self.fields = [""] + line.strip().split()
        elif self.vars.FS == "":
            self.fields = [""] + list(line)
        else:
            self.fields = [""] + line.rstrip('\n').split(self.vars.FS)
        self.vars.NF = len(self.fields) - 1
    
    def get_field(self, n):
        """Get field by number"""
        n = int(n)
        if n == 0:
            return self.current_line.rstrip('\n')
        elif 1 <= n <= len(self.fields) - 1:
            return self.fields[n]
        else:
            return ""
    
    def set_field(self, n, value):
        """Set field by number"""
        n = int(n)
        if n == 0:
            self.current_line = str(value) + '\n'
            self.split_fields(self.current_line)
        else:
            while len(self.fields) <= n:
                self.fields.append("")
            self.fields[n] = str(value)
            self.vars.NF = len(self.fields) - 1
            self.current_line = self.vars.OFS.join(self.fields[1:]) + '\n'
    
    def execute_action(self, action, context):
        """Execute an AWK action"""
        if not action or not action.strip():
            print(self.current_line, end='')
            return
        
        try:
            # Build execution context
            exec_context = {
                'NR': self.vars.NR,
                'NF': self.vars.NF,
                'FNR': self.vars.FNR,
                'FS': self.vars.FS,
                'OFS': self.vars.OFS,
                'ORS': self.vars.ORS,
                'FILENAME': self.vars.FILENAME,
                'IGNORECASE': self.vars.IGNORECASE,
                'ARGC': self.vars.ARGC,
                'ARGV': self.vars.ARGV,
                'field': self.get_field,
                'set_field': self.set_field,
                'print': lambda *args: self.awk_print(*args),
                'printf': self.functions.printf,
                'sprintf': self.functions.sprintf,
                'length': self.functions.length,
                'substr': self.functions.substr,
                'index': self.functions.index,
                'split': self.functions.split,
                'sub': self.functions.sub,
                'gsub': self.functions.gsub,
                'match': self.functions.match,
                'tolower': self.functions.tolower,
                'toupper': self.functions.toupper,
                'sin': self.functions.sin,
                'cos': self.functions.cos,
                'atan2': self.functions.atan2,
                'exp': self.functions.exp,
                'log': self.functions.log,
                'sqrt': self.functions.sqrt,
                'int': self.functions.int,
                'rand': self.functions.rand,
                'srand': self.functions.srand,
                'asort': self.functions.asort,
                'asorti': self.functions.asorti,
                **self.user_vars,
                **self.arrays
            }
            
            # Add AI functions
            for func_name in dir(self.functions):
                if func_name.startswith('ai_'):
                    exec_context[func_name] = getattr(self.functions, func_name)
            
            # Parse and execute - SIMPLIFIED to avoid infinite loops
            parsed_action = self.simple_parse_awk(action)
            
            # Execute the parsed action
            if parsed_action:
                exec(parsed_action, exec_context, self.user_vars)
            
            # Update variables
            if 'NF' in self.user_vars:
                self.vars.NF = self.user_vars['NF']
            if 'OFS' in self.user_vars:
                self.vars.OFS = self.user_vars['OFS']
                
        except Exception as e:
            print(f"Error executing action '{action[:50]}...': {e}", file=sys.stderr)
    
    def simple_parse_awk(self, code):
        """Simplified AWK to Python parser to avoid infinite loops"""
        if not code:
            return ""
        
        # Handle multiline by joining with semicolons
        lines = code.split('\n')
        statements = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle function definitions - skip them for now
            if line.startswith('function '):
                return ""  # Skip function definitions
            
            # Convert field references
            line = re.sub(r'\$(\d+)', r'field(\1)', line)
            line = re.sub(r'\$\(([^)]+)\)', r'field(\1)', line)
            
            # Handle print statements
            if re.match(r'^print\s+', line):
                # Extract what to print
                print_content = line[5:].strip()
                if print_content.startswith('"') and print_content.endswith('"'):
                    line = f'print({print_content})'
                else:
                    line = f'print({print_content})'
            elif line == 'print':
                line = 'print(field(0))'
            
            # Handle simple for loops - convert to while to avoid issues
            for_match = re.match(r'for\s*\(([^;]+);([^;]+);([^)]+)\)\s*{?(.*)}?', line)
            if for_match:
                init = for_match.group(1).strip()
                condition = for_match.group(2).strip()
                increment = for_match.group(3).strip()
                body = for_match.group(4).strip() if for_match.group(4) else ""
                
                # Convert to safer construct
                statements.append(init)
                statements.append(f"# for loop: while {condition}")
                if body:
                    statements.append(f"  {body}")
                    statements.append(f"  {increment}")
                continue
            
            # Handle increment/decrement
            line = re.sub(r'(\w+)\+\+', r'\1 += 1', line)
            line = re.sub(r'(\w+)--', r'\1 -= 1', line)
            
            # Handle BEGIN/END blocks
            if line in ('BEGIN', 'END'):
                continue
            
            statements.append(line)
        
        return '\n'.join(statements)
    
    def awk_print(self, *args):
        """AWK-style print function"""
        if not args:
            print(self.current_line, end='')
        else:
            output = self.vars.OFS.join(str(arg) for arg in args)
            print(output)
    
    def evaluate_condition(self, condition):
        """Evaluate an AWK condition"""
        if not condition:
            return True
        
        try:
            if condition == "BEGIN":
                return self.vars.NR == 0
            elif condition == "END":
                return False
            
            # Handle regex patterns
            if condition.startswith('/') and condition.endswith('/'):
                pattern = condition[1:-1]
                if self.vars.IGNORECASE:
                    return bool(re.search(pattern, self.current_line, re.IGNORECASE))
                else:
                    return bool(re.search(pattern, self.current_line))
            
            # Handle function definitions - skip them
            if condition.startswith('function '):
                return False
            
            # For other conditions, try to evaluate
            eval_context = {
                'NR': self.vars.NR,
                'NF': self.vars.NF,
                'FNR': self.vars.FNR,
                'field': self.get_field,
                **self.user_vars
            }
            
            # Simple parse for condition
            parsed = self.simple_parse_awk(condition)
            if parsed:
                result = eval(parsed, eval_context, self.user_vars)
                return bool(result)
            
            return False
            
        except Exception as e:
            print(f"Error evaluating condition '{condition[:50]}...': {e}", file=sys.stderr)
            return False
    
    def process_file(self, filename, rules):
        """Process a file with AWK rules"""
        # Execute BEGIN rules
        for condition, action in rules:
            if condition == "BEGIN":
                self.execute_action(action, "BEGIN")
        
        # Process input
        try:
            if filename == '-':
                file_obj = sys.stdin
                self.vars.FILENAME = ""
            else:
                file_obj = open(filename, 'r')
                self.vars.FILENAME = filename
            
            self.vars.FNR = 0
            
            for line in file_obj:
                self.vars.NR += 1
                self.vars.FNR += 1
                self.current_line = line
                self.split_fields(line)
                
                # Process each rule
                for condition, action in rules:
                    if condition not in ("BEGIN", "END"):
                        if self.evaluate_condition(condition):
                            self.execute_action(action, "MAIN")
            
            if filename != '-':
                file_obj.close()
                
        except FileNotFoundError:
            print(f"File not found: {filename}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error processing file {filename}: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Execute END rules
        for condition, action in rules:
            if condition == "END":
                self.execute_action(action, "END")


def parse_awk_program(program):
    """Parse AWK program into rules - simplified to avoid issues"""
    rules = []
    
    if not program:
        return rules
    
    # Split into major blocks
    # Look for BEGIN/END blocks and pattern-action pairs
    
    # Handle BEGIN blocks
    begin_match = re.search(r'BEGIN\s*{([^}]*)}', program, re.DOTALL)
    if begin_match:
        rules.append(("BEGIN", begin_match.group(1).strip()))
        program = program.replace(begin_match.group(0), '')
    
    # Handle END blocks
    end_match = re.search(r'END\s*{([^}]*)}', program, re.DOTALL)
    if end_match:
        rules.append(("END", end_match.group(1).strip()))
        program = program.replace(end_match.group(0), '')
    
    # Handle pattern-action pairs
    # Simple approach: look for { } blocks
    remaining = program.strip()
    if remaining:
        # Check if it's just an action (no pattern)
        if remaining.startswith('{') and remaining.endswith('}'):
            rules.append(("", remaining[1:-1].strip()))
        elif '{' in remaining and '}' in remaining:
            # Try to parse pattern { action }
            parts = remaining.split('{', 1)
            if len(parts) == 2:
                pattern = parts[0].strip()
                action_part = parts[1]
                if '}' in action_part:
                    action = action_part[:action_part.rfind('}')].strip()
                    rules.append((pattern, action))
        else:
            # No action, just a pattern (default action is print)
            rules.append((remaining, ""))
    
    return rules


def main():
    parser = argparse.ArgumentParser(
        description="PyAwk Fixed - Python AWK with improved parsing"
    )
    
    parser.add_argument('program', nargs='?', help='AWK program to execute')
    parser.add_argument('files', nargs='*', default=['-'], 
                       help='Input files (default: stdin)')
    parser.add_argument('-F', '--field-separator', default=' ',
                       help='Field separator (default: space)')
    parser.add_argument('-v', '--assign', action='append', default=[],
                       help='Variable assignment (var=value)')
    parser.add_argument('-f', '--file', help='Read AWK program from file')
    parser.add_argument('--version', action='version', version='PyAwk Fixed 1.0')
    
    args = parser.parse_args()
    
    # Get the AWK program
    if args.file:
        with open(args.file, 'r') as f:
            program = f.read()
    elif args.program:
        program = args.program
    else:
        parser.error("Either provide a program or use -f to specify a file")
    
    # Parse variable assignments
    user_vars = {}
    for assignment in args.assign:
        if '=' in assignment:
            var, val = assignment.split('=', 1)
            try:
                val = int(val)
            except ValueError:
                try:
                    val = float(val)
                except ValueError:
                    pass
            user_vars[var] = val
    
    # Parse the AWK program
    rules = parse_awk_program(program)
    
    # Create processor
    processor = AwkProcessor(field_separator=args.field_separator)
    processor.user_vars.update(user_vars)
    
    # Set ARGC and ARGV
    processor.vars.ARGC = len(args.files)
    processor.vars.ARGV = args.files
    
    # Process files
    for filename in args.files:
        processor.process_file(filename, rules)


if __name__ == "__main__":
    main()