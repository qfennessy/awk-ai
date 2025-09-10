# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

PyAwk is a Python implementation of the AWK programming language enhanced with AI capabilities. It provides both traditional AWK functionality (pattern matching, field processing, built-in variables) and modern AI features (sentiment analysis, text classification, translation, entity extraction).

## Common Commands

### Running PyAwk
```bash
# Basic usage
python3 pyawk_ai.py '{print}' file.txt

# With field separator
python3 pyawk_ai.py -F, '{print field(1), field(3)}' data.csv

# Pattern matching
python3 pyawk_ai.py '/pattern/ {print}' file.txt

# AI sentiment analysis
python3 pyawk_ai.py '{sentiment = ai_sentiment(field(0)); print field(0), "→", sentiment}' text.txt

# Test the script
echo "Test data" | python3 pyawk_ai.py '{print field(0)}'
```

### Development Tasks
```bash
# Make script executable
chmod +x pyawk_ai.py

# Run help
python3 pyawk_ai.py --help
```

## Architecture

### Core Components

1. **AwkVariables** (pyawk_ai.py:20-49): Container for AWK built-in variables (NR, NF, FS, OFS, etc.)

2. **AwkFunctions** (pyawk_ai.py:52-293): Implementation of both traditional AWK functions and AI-enhanced functions
   - Traditional: `length()`, `substr()`, `toupper()`, `tolower()`, math functions
   - AI functions: `ai_sentiment()`, `ai_classify()`, `ai_translate()`, `ai_summarize()`, `ai_entity_extract()`, etc.
   - AI functions currently use simulated responses for demo (pyawk_ai.py:56-134)

3. **AwkProcessor** (pyawk_ai.py:296-518): Main processing engine
   - Handles field splitting with configurable separators
   - Manages execution context and user variables
   - Processes BEGIN/END blocks and pattern-action rules
   - Field access via `field(n)` function (equivalent to AWK's $n)

4. **Parser** (pyawk_ai.py:521-572): Parses AWK program syntax into executable rules

### Key Design Decisions

- Fields accessed via `field(n)` function instead of $n syntax for Python compatibility
- AI functions use simulated responses for demo purposes but structured for easy API integration
- Pattern matching supports both regex (/pattern/) and conditional expressions
- User variables auto-initialize to 0 when undefined (AWK behavior)

## Important Notes

- Python 3.6+ required (uses f-strings)
- AI functions return simulated responses - can be integrated with real AI APIs
- Field indexing: field(0) = entire record, field(1) = first field, etc.
- Default field separator is space, handles multiple whitespace
- Supports BEGIN/END blocks, pattern-action rules, and user-defined variables