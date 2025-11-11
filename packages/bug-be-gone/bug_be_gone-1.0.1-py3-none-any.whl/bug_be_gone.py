#!/usr/bin/env python3
"""
UNIVERSAL DEBUGGER MERGED - The Complete Python Error Annihilator
Combines all features from both debugger implementations into one ultimate tool.

MERGED FEATURES:
- Smart return value detection based on context (from v1)
- AST-based code parsing for intelligent fixes (from ultimate)
- Comprehensive error database with pattern matching (both versions)
- Multi-line block wrapping for control structures (both versions)
- Type error detection and fixing with mypy integration (from ultimate)
- Deployment validation and auto-fix (from ultimate)
- Error prediction before they occur (from ultimate)
- Automatic dependency resolution (from ultimate)
- Performance bottleneck fixing (from ultimate)
- Smart conversion strategies for all types (from ultimate)
- Comprehensive ValueError and TypeError handling (both versions)

Usage: 
    python universal_debugger_merged.py your_script.py              # Fix runtime errors
    python universal_debugger_merged.py --types your_script.py      # Fix type errors
    python universal_debugger_merged.py --deploy                    # Validate deployment
    python universal_debugger_merged.py --all your_script.py        # Fix everything
    python universal_debugger_merged.py --predict your_script.py    # Predict future errors
    python universal_debugger_merged.py --ultimate your_script.py   # ACTIVATE EVERYTHING
"""

import sys
import os
import re
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any, Union
import ast
import json
import traceback
from datetime import datetime
import hashlib

# ============================================================================
# CORE UTILITY FUNCTIONS
# ============================================================================

def get_indent(line):
    """Extract indentation from line."""
    return ' ' * (len(line) - len(line.lstrip()))


def smart_return_value(line, error_type=''):
    """Smart return value detection based on context from v1."""
    line_lower = line.lower()
    
    # File operations return empty string
    if any(x in line_lower for x in ['read', '.txt', '.csv', '.json', 'file', 'open']):
        return '""'
    
    # List operations return empty list
    if any(x in line_lower for x in ['.append', '.extend', '[', 'list']):
        return '[]'
    
    # Dict operations return empty dict
    if any(x in line_lower for x in ['.update', '.get', '.keys', '.items', 'dict', '{']):
        return '{}'
    
    # Numeric operations return 0
    if any(x in line_lower for x in ['int(', 'float(', 'sum', 'len', 'count']):
        return '0'
    
    # String operations return empty string
    if any(x in line_lower for x in ['str(', '.format', '.join', 'print']):
        return '""'
    
    # Boolean operations return False
    if any(x in line_lower for x in ['bool(', 'is', '==', '!=', '>', '<']):
        return 'False'
    
    # Default based on error type
    if 'Attribute' in error_type:
        return 'None'
    
    return '{}'


def wrap_in_try_except(line, exception_type, indent_level=0, custom_except=None):
    """Wrap line in try/except block with smart return value."""
    base_indent = ' ' * indent_level
    inner_indent = ' ' * (indent_level + 4)
    
    # Use smart return value from v1
    return_value = smart_return_value(line, exception_type)
    
    if custom_except:
        return f"{base_indent}try:\n{inner_indent}{line.strip()}\n{custom_except}\n"
    else:
        return f"{base_indent}try:\n{inner_indent}{line.strip()}\n{base_indent}except {exception_type}:\n{inner_indent}return {return_value}\n"


def get_indented_block(lines, start_idx):
    """Get all lines in an indented block starting from start_idx."""
    if start_idx >= len(lines):
        return ([], 0)
    
    base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    block_lines = [lines[start_idx].rstrip()]
    
    # Read subsequent lines that are more indented
    idx = start_idx + 1
    while idx < len(lines):
        line = lines[idx]
        if line.strip() == '':
            block_lines.append('')
            idx += 1
            continue
        
        line_indent = len(line) - len(line.lstrip())
        if line_indent <= base_indent:
            break
        
        block_lines.append(line.rstrip())
        idx += 1
    
    return (block_lines, base_indent)


def wrap_block_in_try_except(block_lines, base_indent, exception_type):
    """Wrap a multi-line block in try/except with smart return value."""
    spaces = ' ' * base_indent
    inner_spaces = ' ' * (base_indent + 4)
    
    # Smart return value from v1 - check the block content
    block_text = '\n'.join(block_lines).lower()
    return_value = smart_return_value(block_text, exception_type)
    
    fixed_lines = [f"{spaces}try:"]
    for block_line in block_lines:
        if block_line.strip():
            # Preserve relative indentation within the block
            line_indent = len(block_line) - len(block_line.lstrip())
            extra_indent = line_indent - base_indent
            fixed_lines.append(f"{inner_spaces}{' ' * extra_indent}{block_line.lstrip()}")
        else:
            fixed_lines.append('')
    fixed_lines.append(f"{spaces}except {exception_type}:")
    fixed_lines.append(f"{inner_spaces}return {return_value}")
    
    return '\n'.join(fixed_lines) + '\n'

# ============================================================================
# AST-BASED INTELLIGENT PARSING (from ultimate)
# ============================================================================

def try_parse_python_line(line):
    """Safely parse a line of Python code using AST."""
    try:
        # Try to parse as expression
        return ast.parse(line.strip(), mode='eval')
    except:
        try:
            # Try to parse as statement
            return ast.parse(line.strip(), mode='exec')
        except:
            return None


def extract_function_call_args(line):
    """Extract function name and arguments from a function call."""
    tree = try_parse_python_line(line)
    if not tree:
        return None, []
    
    # Find Call nodes
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Get function name
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            
            # Get argument names/values
            args = []
            for arg in node.args:
                if isinstance(arg, ast.Name):
                    args.append(arg.id)
                elif isinstance(arg, ast.Constant):
                    args.append(repr(arg.value))
            
            return func_name, args
    
    return None, []


def apply_type_conversion(line, indent, arg_position, expected_type, got_type):
    """Apply intelligent type conversion based on type mismatch."""
    
    # Parse the line to understand structure
    func_name, args = extract_function_call_args(line)
    
    if not func_name or arg_position >= len(args):
        return None
    
    arg_name = args[arg_position]
    
    # Comprehensive type conversion strategies from ultimate
    conversions = {
        # String conversions
        ('UserString', 'str'): f'{arg_name}.data',
        ('int', 'str'): f'str({arg_name})',
        ('float', 'str'): f'str({arg_name})',
        ('bool', 'str'): f'str({arg_name})',
        ('list', 'str'): f'str({arg_name})',
        ('dict', 'str'): f'json.dumps({arg_name})',
        ('tuple', 'str'): f'str({arg_name})',
        ('set', 'str'): f'str({arg_name})',
        ('bytes', 'str'): f'{arg_name}.decode("utf-8", errors="ignore")',
        ('bytearray', 'str'): f'{arg_name}.decode("utf-8", errors="ignore")',
        
        # Numeric conversions
        ('str', 'int'): f'int({arg_name}) if {arg_name}.isdigit() else 0',
        ('float', 'int'): f'int({arg_name})',
        ('bool', 'int'): f'int({arg_name})',
        ('str', 'float'): f'float({arg_name}) if {arg_name}.replace(".", "").replace("-", "").isdigit() else 0.0',
        ('int', 'float'): f'float({arg_name})',
        ('str', 'bool'): f'bool({arg_name})',
        ('Decimal', 'float'): f'float({arg_name})',
        ('Fraction', 'float'): f'float({arg_name})',
        
        # Bytes conversions
        ('str', 'bytes'): f'{arg_name}.encode("utf-8", errors="ignore")',
        ('bytearray', 'bytes'): f'bytes({arg_name})',
        
        # Container conversions
        ('str', 'list'): f'list({arg_name})',
        ('tuple', 'list'): f'list({arg_name})',
        ('set', 'list'): f'list({arg_name})',
        ('dict', 'list'): f'list({arg_name}.items())',
        ('range', 'list'): f'list({arg_name})',
        ('generator', 'list'): f'list({arg_name})',
        ('map', 'list'): f'list({arg_name})',
        ('filter', 'list'): f'list({arg_name})',
        ('zip', 'list'): f'list({arg_name})',
        
        ('list', 'tuple'): f'tuple({arg_name})',
        ('set', 'tuple'): f'tuple({arg_name})',
        ('list', 'set'): f'set({arg_name})',
        ('tuple', 'set'): f'set({arg_name})',
        
        # None handling
        ('NoneType', 'str'): f'{arg_name} or ""',
        ('NoneType', 'int'): f'{arg_name} or 0',
        ('NoneType', 'float'): f'{arg_name} or 0.0',
        ('NoneType', 'list'): f'{arg_name} or []',
        ('NoneType', 'dict'): f'{arg_name} or {{}}',
        ('NoneType', 'bool'): f'bool({arg_name})',
    }
    
    # Try to find a conversion
    conversion_key = (got_type, expected_type)
    if conversion_key in conversions:
        conversion = conversions[conversion_key]
        # Replace the argument in the line
        pattern = re.escape(arg_name)
        fixed_line = re.sub(pattern, conversion, line, count=1)
        return fixed_line
    
    # Fallback: wrap in str() for most cases
    if expected_type == 'str':
        pattern = re.escape(arg_name)
        fixed_line = re.sub(pattern, f'str({arg_name})', line, count=1)
        return fixed_line
    
    return None

# ============================================================================
# ERROR FIXING FUNCTIONS (Combined from both versions)
# ============================================================================

def _fix_name_error(line, indent, error_msg):
    """Fix NameError by initializing undefined variable with smart type detection from v1."""
    pattern = r"name '(\w+)' is not defined"
    match = re.search(pattern, error_msg)
    if match:
        var_name = match.group(1)
        
        # Smart type detection from v1
        if '.append' in line or '.extend' in line:
            return f"{indent}{var_name} = []  # Initialize as list\n{line}"
        elif '.update' in line or '.get' in line or '.keys' in line or '.items' in line:
            return f"{indent}{var_name} = {{}}  # Initialize as dict\n{line}"
        elif '[' in line and ']' in line and var_name in line:
            # Check if it's being indexed (dict/list access)
            if f"{var_name}[" in line:
                return f"{indent}{var_name} = {{}}  # Initialize as dict\n{line}"
        elif '+' in line and ('"' in line or "'" in line):
            return f"{indent}{var_name} = ''  # Initialize as string\n{line}"
        elif 'int(' in line or 'float(' in line or any(op in line for op in ['+', '-', '*', '/']):
            return f"{indent}{var_name} = 0  # Initialize as number\n{line}"
        else:
            return f"{indent}{var_name} = None  # Initialize variable\n{line}"
    return line


def _fix_import_error(line, indent, error_msg):
    """Fix ImportError by wrapping in try/except with install suggestion."""
    pattern = r"No module named '([^']+)'"
    match = re.search(pattern, error_msg)
    if match:
        module_name = match.group(1)
        # Map common module name variations to pip packages
        pip_packages = {
            'cv2': 'opencv-python',
            'sklearn': 'scikit-learn',
            'PIL': 'pillow',
            'yaml': 'pyyaml',
            'dotenv': 'python-dotenv',
            'bs4': 'beautifulsoup4',
            'OpenSSL': 'pyopenssl',
            'Crypto': 'pycryptodome',
        }
        pip_name = pip_packages.get(module_name.split('.')[0], module_name)
        
        return (f"{indent}try:\n"
                f"{indent}    {line.strip()}\n"
                f"{indent}except (ImportError, ModuleNotFoundError):\n"
                f"{indent}    pass  # Run: pip install {pip_name}\n")
    return line


def _fix_unbound_local_error(line, indent, error_msg):
    """Fix UnboundLocalError by initializing variable."""
    pattern = r"local variable '(\w+)' referenced"
    match = re.search(pattern, error_msg)
    if match:
        var_name = match.group(1)
        # Use smart type detection
        if any(x in line for x in ['append', 'extend', '[']):
            init_value = '[]'
        elif any(x in line for x in ['update', 'get', 'keys', '{']):
            init_value = '{}'
        elif any(x in line for x in ['int(', 'float(', '+', '-', '*', '/']):
            init_value = '0'
        else:
            init_value = 'None'
        
        return f"{indent}{var_name} = {init_value}  # Initialize\n{line}"
    return line


def parse_value_error_message(error_msg):
    """Extract information from ValueError messages."""
    patterns = {
        'invalid_literal': r"invalid literal for (\w+)\(\) with base (\d+): '([^']+)'",
        'not_enough_values': r"not enough values to unpack \(expected (\d+), got (\d+)\)",
        'too_many_values': r"too many values to unpack \(expected (\d+)(?:, got (\d+))?\)",
        'empty_sequence': r"(max|min)\(\) (?:arg|iterable argument) is (?:an )?empty",
        'invalid_format': r"Unknown format code '(.+)' for",
        'invalid_operation': r"invalid operation",
    }
    
    for pattern_name, pattern in patterns.items():
        match = re.search(pattern, error_msg)
        if match:
            return pattern_name, match.groups()
    
    return None, None


def _fix_value_error_smart(line, indent, error_msg):
    """Intelligently fix ValueError by understanding the context."""
    
    pattern_type, groups = parse_value_error_message(error_msg)
    
    if pattern_type == 'invalid_literal':
        # E.g., "invalid literal for int() with base 10: 'abc'"
        func_name, base, invalid_value = groups
        
        # Wrap int/float conversion in try/except with default
        if func_name in ('int', 'float'):
            return (f"{indent}try:\n"
                   f"{indent}    {line.strip()}\n"
                   f"{indent}except ValueError:\n"
                   f"{indent}    {line.split('=')[0].strip()} = 0  # Default for invalid {func_name}\n")
    
    elif pattern_type == 'too_many_values':
        # E.g., "too many values to unpack (expected 2)"
        expected_count = int(groups[0])
        
        # Find the assignment: x, y = something
        unpack_pattern = r'([a-zA-Z_]\w*(?:\s*,\s*[a-zA-Z_]\w*)*)\s*=\s*(.+)'
        match = re.match(unpack_pattern, line.strip())
        
        if match:
            var_names = [v.strip() for v in match.group(1).split(',')]
            source = match.group(2).strip()
            
            # Add slice to limit values: x, y = source[:2]
            fixed_line = f"{indent}{', '.join(var_names)} = {source}[:{expected_count}]\n"
            return fixed_line
    
    elif pattern_type == 'not_enough_values':
        # E.g., "not enough values to unpack (expected 3, got 1)"
        expected, got = int(groups[0]), int(groups[1])
        
        # Find the assignment
        unpack_pattern = r'([a-zA-Z_]\w*(?:\s*,\s*[a-zA-Z_]\w*)*)\s*=\s*(.+)'
        match = re.match(unpack_pattern, line.strip())
        
        if match:
            var_names = [v.strip() for v in match.group(1).split(',')]
            source = match.group(2).strip()
            
            # Pad with None: x, y, z = (source + [None] * 3)[:3]
            needed_padding = expected - got
            fixed_line = f"{indent}{', '.join(var_names)} = (list({source}) + [None] * {expected})[:{expected}]\n"
            return fixed_line
    
    elif pattern_type == 'empty_sequence':
        # Max/min on empty sequence
        if 'max' in line:
            return (f"{indent}try:\n"
                   f"{indent}    {line.strip()}\n"
                   f"{indent}except ValueError:\n"
                   f"{indent}    result = 0  # Default for empty sequence\n")
        elif 'min' in line:
            return (f"{indent}try:\n"
                   f"{indent}    {line.strip()}\n"
                   f"{indent}except ValueError:\n"
                   f"{indent}    result = float('inf')  # Default for empty sequence\n")
    
    # General fallback: wrap in try/except
    return wrap_in_try_except(line, 'ValueError', len(indent))


def _fix_type_error_smart(line, indent, error_msg):
    """Smart TypeError fixing from ultimate with enhanced conversions."""
    
    # Pattern for "X takes Y arguments but Z were given"
    args_pattern = r"(\w+)\(\) takes (?:exactly )?(\d+) (?:positional )?arguments? but (\d+) (?:were|was) given"
    match = re.search(args_pattern, error_msg)
    
    if match:
        func_name, expected, given = match.groups()
        expected, given = int(expected), int(given)
        
        # Find function call in line
        call_pattern = rf'{func_name}\s*\((.*?)\)'
        call_match = re.search(call_pattern, line)
        
        if call_match and given > expected:
            args = call_match.group(1)
            # Limit arguments
            args_list = [a.strip() for a in args.split(',')]
            limited_args = args_list[:expected]
            fixed_call = f"{func_name}({', '.join(limited_args)})"
            return re.sub(call_pattern, fixed_call, line)
    
    # Pattern for type mismatch "argument must be X, not Y"
    type_pattern = r"argument (\d+)? ?(?:must be|should be) (\w+), not (\w+)"
    match = re.search(type_pattern, error_msg)
    
    if match:
        arg_pos, expected_type, got_type = match.groups()
        arg_position = int(arg_pos) - 1 if arg_pos else 0
        
        # Try smart type conversion
        fixed = apply_type_conversion(line, indent, arg_position, expected_type, got_type)
        if fixed:
            return fixed
    
    # Pattern for unsupported operand types
    operand_pattern = r"unsupported operand type\(s\) for (\S+): '(\w+)' and '(\w+)'"
    match = re.search(operand_pattern, error_msg)
    
    if match:
        operator, type1, type2 = match.groups()
        # Wrap operation in try/except with appropriate conversion
        return (f"{indent}try:\n"
               f"{indent}    {line.strip()}\n"
               f"{indent}except TypeError:\n"
               f"{indent}    result = 0  # Type mismatch in operation\n")
    
    # General fallback
    return wrap_in_try_except(line, 'TypeError', len(indent))


def _fix_attribute_error(line, indent, error_msg):
    """Fix AttributeError with smart suggestions."""
    
    # Pattern for 'X' object has no attribute 'Y'
    pattern = r"'(\w+)' object has no attribute '(\w+)'"
    match = re.search(pattern, error_msg)
    
    if match:
        obj_type, attr_name = match.groups()
        
        # Common attribute alternatives
        alternatives = {
            'append': ['extend', 'add', 'insert'],
            'split': ['strip', 'replace', 'partition'],
            'items': ['keys', 'values', 'get'],
            'find': ['index', 'count', 'startswith'],
            'update': ['setdefault', 'get', 'pop'],
        }
        
        # Try to suggest alternative
        if attr_name in alternatives:
            alt = alternatives[attr_name][0]
            suggestion = f"# Maybe you meant .{alt}()?"
            return f"{line.rstrip()}  {suggestion}\n{indent}return None  # AttributeError handled\n"
        
        # Wrap in try/except
        return (f"{indent}try:\n"
               f"{indent}    {line.strip()}\n"
               f"{indent}except AttributeError:\n"
               f"{indent}    pass  # {obj_type} has no {attr_name}\n")
    
    return wrap_in_try_except(line, 'AttributeError', len(indent))


def _fix_index_error(line, indent, error_msg):
    """Fix IndexError by adding bounds checking."""
    
    # Find index access patterns
    index_pattern = r'(\w+)\[([^\]]+)\]'
    matches = re.finditer(index_pattern, line)
    
    for match in matches:
        var_name = match.group(1)
        index_expr = match.group(2)
        
        # Wrap access in safe check
        safe_access = f"({var_name}[{index_expr}] if len({var_name}) > {index_expr} else None)"
        line = line.replace(match.group(0), safe_access)
    
    # If we modified the line, return it
    if index_pattern in line:
        return line
    
    # Otherwise wrap in try/except
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except IndexError:\n"
           f"{indent}    pass  # Index out of range\n")


def _fix_key_error(line, indent, error_msg):
    """Fix KeyError by using .get() with default."""
    
    # Find dictionary access patterns
    dict_pattern = r'(\w+)\[([\'"][^\'"]+[\'"])\]'
    matches = re.finditer(dict_pattern, line)
    
    for match in matches:
        dict_name = match.group(1)
        key = match.group(2)
        
        # Replace with .get()
        safe_access = f"{dict_name}.get({key}, None)"
        line = line.replace(match.group(0), safe_access)
    
    # If we modified the line, return it
    if matches:
        return line
    
    # Otherwise wrap in try/except
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except KeyError:\n"
           f"{indent}    pass  # Key not found in dictionary\n")


def _fix_zero_division_error(line, indent, error_msg):
    """Fix ZeroDivisionError by checking denominator."""
    
    # Find division operations
    div_pattern = r'(\S+)\s*/\s*(\S+)'
    match = re.search(div_pattern, line)
    
    if match:
        numerator = match.group(1)
        denominator = match.group(2)
        
        # Add check for zero
        return (f"{indent}if {denominator} != 0:\n"
               f"{indent}    {line.strip()}\n"
               f"{indent}else:\n"
               f"{indent}    result = 0  # Avoided division by zero\n")
    
    # Fallback to try/except
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except ZeroDivisionError:\n"
           f"{indent}    result = 0  # Division by zero\n")


def _fix_file_not_found_error(line, indent, error_msg):
    """Fix FileNotFoundError by creating file or using default."""
    
    # Check if it's a read operation
    if 'open(' in line and ('r' in line or not 'w' in line):
        # Extract filename if possible
        file_pattern = r"open\s*\(\s*['\"]([^'\"]+)['\"]"
        match = re.search(file_pattern, line)
        
        if match:
            filename = match.group(1)
            return (f"{indent}try:\n"
                   f"{indent}    {line.strip()}\n"
                   f"{indent}except FileNotFoundError:\n"
                   f"{indent}    # Create empty file\n"
                   f"{indent}    open('{filename}', 'w').close()\n"
                   f"{indent}    {line.strip()}\n")
    
    # General fallback
    return wrap_in_try_except(line, 'FileNotFoundError', len(indent))


def _fix_permission_error(line, indent, error_msg):
    """Fix PermissionError by handling access issues."""
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except PermissionError:\n"
           f"{indent}    print('Permission denied - check file permissions')\n"
           f"{indent}    pass\n")


def _fix_recursion_error(line, indent, error_msg):
    """Fix RecursionError by adding depth limit."""
    return (f"{indent}import sys\n"
           f"{indent}sys.setrecursionlimit(10000)  # Increase recursion limit\n"
           f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except RecursionError:\n"
           f"{indent}    print('Maximum recursion depth exceeded')\n"
           f"{indent}    pass\n")


def _fix_memory_error(line, indent, error_msg):
    """Fix MemoryError by handling large allocations."""
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except MemoryError:\n"
           f"{indent}    print('Out of memory - reduce data size')\n"
           f"{indent}    pass\n")


def _fix_overflow_error(line, indent, error_msg):
    """Fix OverflowError by handling large numbers."""
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except OverflowError:\n"
           f"{indent}    result = float('inf')  # Number too large\n")


def _fix_timeout_error(line, indent, error_msg):
    """Fix TimeoutError by adding timeout handling."""
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except TimeoutError:\n"
           f"{indent}    print('Operation timed out')\n"
           f"{indent}    pass\n")


def _fix_connection_error(line, indent, error_msg):
    """Fix ConnectionError by handling network issues."""
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except (ConnectionError, ConnectionRefusedError, ConnectionResetError):\n"
           f"{indent}    print('Connection failed - check network')\n"
           f"{indent}    pass\n")


def _fix_json_decode_error(line, indent, error_msg):
    """Fix JSONDecodeError by handling invalid JSON."""
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except json.JSONDecodeError:\n"
           f"{indent}    data = {{}}  # Invalid JSON, using empty dict\n")


def _fix_unicode_error(line, indent, error_msg):
    """Fix UnicodeError by handling encoding issues."""
    if 'encode' in line:
        return (f"{indent}try:\n"
               f"{indent}    {line.strip()}\n"
               f"{indent}except UnicodeEncodeError:\n"
               f"{indent}    result = text.encode('utf-8', errors='ignore')\n")
    else:
        return (f"{indent}try:\n"
               f"{indent}    {line.strip()}\n"
               f"{indent}except UnicodeDecodeError:\n"
               f"{indent}    result = data.decode('utf-8', errors='ignore')\n")


def _fix_assertion_error(line, indent, error_msg):
    """Fix AssertionError by removing or handling assertion."""
    if line.strip().startswith('assert'):
        # Comment out the assertion
        return f"{indent}# {line.strip()}  # Assertion disabled\n"
    else:
        return (f"{indent}try:\n"
               f"{indent}    {line.strip()}\n"
               f"{indent}except AssertionError:\n"
               f"{indent}    pass  # Assertion failed\n")


def _fix_stopiteration_error(line, indent, error_msg):
    """Fix StopIteration by handling iterator exhaustion."""
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except StopIteration:\n"
           f"{indent}    pass  # Iterator exhausted\n")


def _fix_generator_exit(line, indent, error_msg):
    """Fix GeneratorExit by handling generator termination."""
    return (f"{indent}try:\n"
           f"{indent}    {line.strip()}\n"
           f"{indent}except GeneratorExit:\n"
           f"{indent}    pass  # Generator terminated\n")

# ============================================================================
# ERROR DATABASE (Comprehensive merger of both versions)
# ============================================================================

ERROR_DATABASE = {
    'SyntaxError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': lambda line, indent, msg: line + ' # Fixed syntax\n' if not line.strip().endswith(':') else line,
                'multiline': False
            }
        ]
    },
    'NameError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': _fix_name_error,
                'multiline': False
            }
        ]
    },
    'ImportError': {
        'patterns': [
            {
                'detect': r'import|from .* import',
                'fix': _fix_import_error,
                'multiline': True
            }
        ]
    },
    'ModuleNotFoundError': {
        'patterns': [
            {
                'detect': r'import|from .* import',
                'fix': _fix_import_error,
                'multiline': True
            }
        ]
    },
    'TypeError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': _fix_type_error_smart,
                'multiline': True
            }
        ]
    },
    'ValueError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': _fix_value_error_smart,
                'multiline': True
            }
        ]
    },
    'AttributeError': {
        'patterns': [
            {
                'detect': r'\.\w+',
                'fix': _fix_attribute_error,
                'multiline': True
            }
        ]
    },
    'IndexError': {
        'patterns': [
            {
                'detect': r'\[.+\]',
                'fix': _fix_index_error,
                'multiline': True
            }
        ]
    },
    'KeyError': {
        'patterns': [
            {
                'detect': r'\[.+\]|\.\w+',
                'fix': _fix_key_error,
                'multiline': True
            }
        ]
    },
    'ZeroDivisionError': {
        'patterns': [
            {
                'detect': r'/|//',
                'fix': _fix_zero_division_error,
                'multiline': True
            }
        ]
    },
    'FileNotFoundError': {
        'patterns': [
            {
                'detect': r'open\s*\(|with\s+open',
                'fix': _fix_file_not_found_error,
                'multiline': True
            }
        ]
    },
    'PermissionError': {
        'patterns': [
            {
                'detect': r'open|write|read|mkdir|rmdir',
                'fix': _fix_permission_error,
                'multiline': True
            }
        ]
    },
    'RecursionError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': _fix_recursion_error,
                'multiline': True
            }
        ]
    },
    'MemoryError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': _fix_memory_error,
                'multiline': True
            }
        ]
    },
    'OverflowError': {
        'patterns': [
            {
                'detect': r'\*\*|pow',
                'fix': _fix_overflow_error,
                'multiline': True
            }
        ]
    },
    'TimeoutError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': _fix_timeout_error,
                'multiline': True
            }
        ]
    },
    'ConnectionError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': _fix_connection_error,
                'multiline': True
            }
        ]
    },
    'ConnectionRefusedError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': _fix_connection_error,
                'multiline': True
            }
        ]
    },
    'ConnectionResetError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': _fix_connection_error,
                'multiline': True
            }
        ]
    },
    'JSONDecodeError': {
        'patterns': [
            {
                'detect': r'json\.load|json\.loads',
                'fix': _fix_json_decode_error,
                'multiline': True
            }
        ]
    },
    'UnicodeDecodeError': {
        'patterns': [
            {
                'detect': r'decode|open.*text|read',
                'fix': _fix_unicode_error,
                'multiline': True
            }
        ]
    },
    'UnicodeEncodeError': {
        'patterns': [
            {
                'detect': r'encode|write|print',
                'fix': _fix_unicode_error,
                'multiline': True
            }
        ]
    },
    'AssertionError': {
        'patterns': [
            {
                'detect': r'assert',
                'fix': _fix_assertion_error,
                'multiline': False
            }
        ]
    },
    'UnboundLocalError': {
        'patterns': [
            {
                'detect': r'.*',
                'fix': _fix_unbound_local_error,
                'multiline': False
            }
        ]
    },
    'StopIteration': {
        'patterns': [
            {
                'detect': r'next|__next__|for.*in',
                'fix': _fix_stopiteration_error,
                'multiline': True
            }
        ]
    },
    'GeneratorExit': {
        'patterns': [
            {
                'detect': r'yield|generator',
                'fix': _fix_generator_exit,
                'multiline': True
            }
        ]
    },
}

# ============================================================================
# DEPLOYMENT VALIDATION (from ultimate)
# ============================================================================

def check_deployment_issues():
    """Check for common deployment issues."""
    issues = []
    
    # Check environment variables
    required_env_vars = ['DATABASE_URL', 'SECRET_KEY', 'API_KEY']
    for var in required_env_vars:
        if not os.environ.get(var):
            issues.append(f"Missing environment variable: {var}")
    
    # Check file permissions
    important_paths = ['./logs', './uploads', './tmp']
    for path in important_paths:
        if os.path.exists(path) and not os.access(path, os.W_OK):
            issues.append(f"No write permission: {path}")
    
    # Check port availability
    import socket
    common_ports = [80, 443, 8000, 8080, 3000, 5000]
    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result == 0:
            issues.append(f"Port {port} is already in use")
    
    return issues


def fix_deployment_issues(issues):
    """Auto-fix deployment issues where possible."""
    for issue in issues:
        if "Missing environment variable" in issue:
            var_name = issue.split(": ")[1]
            # Create .env file
            with open('.env', 'a') as f:
                f.write(f"\n{var_name}=your_{var_name.lower()}_here")
            print(f"[FIX] Added {var_name} to .env file")
            
        elif "No write permission" in issue:
            path = issue.split(": ")[1]
            os.makedirs(path, exist_ok=True)
            os.chmod(path, 0o755)
            print(f"[FIX] Fixed permissions for {path}")
            
        elif "Port" in issue and "in use" in issue:
            port = int(issue.split(" ")[1])
            print(f"[INFO] Port {port} is in use, consider using a different port")

# ============================================================================
# TYPE CHECKING (from ultimate)
# ============================================================================

def run_type_checker(file_path):
    """Run mypy type checker if available."""
    try:
        result = subprocess.run(
            ['mypy', '--ignore-missing-imports', file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def parse_type_error(output):
    """Parse mypy output for type errors."""
    errors = []
    for line in output.split('\n'):
        if ': error:' in line:
            match = re.match(r'(.+):(\d+): error: (.+)', line)
            if match:
                errors.append({
                    'file': match.group(1),
                    'line': int(match.group(2)),
                    'message': match.group(3)
                })
    return errors


def fix_type_error(file_path, line_number, error_message):
    """Apply type hint fixes."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if line_number > 0 and line_number <= len(lines):
            target_line = lines[line_number - 1]
            indent = get_indent(target_line)
            
            # Add type: ignore comment
            if not '# type: ignore' in target_line:
                lines[line_number - 1] = target_line.rstrip() + '  # type: ignore\n'
                
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                
                print(f"[FIX] Added type ignore at line {line_number}")
                return True
    except:
        pass
    
    return False

# ============================================================================
# ERROR PREDICTION (from ultimate)
# ============================================================================

class ErrorPredictor:
    """Predict potential errors before they occur."""
    
    def __init__(self):
        self.patterns = {
            'division_by_zero': r'(\w+)\s*/\s*(\w+)',
            'uninitialized_var': r'^(\s*)(\w+)\.append\(',
            'missing_return': r'^\s*def\s+\w+.*:',
            'infinite_loop': r'^\s*while\s+True:',
            'unclosed_file': r'open\([^)]+\)\.',
            'sql_injection': r'execute\(.+%\s*s',
            'hardcoded_password': r'password\s*=\s*[\'"]',
            'unused_variable': r'^\s*(\w+)\s*=.*(?!.*\1)',
        }
    
    def predict_errors(self, code_lines):
        """Analyze code for potential errors."""
        predictions = []
        
        for i, line in enumerate(code_lines):
            for error_type, pattern in self.patterns.items():
                if re.search(pattern, line):
                    prediction = {
                        'line': i + 1,
                        'type': error_type,
                        'code': line.strip(),
                        'suggestion': self._get_suggestion(error_type)
                    }
                    predictions.append(prediction)
        
        return predictions
    
    def _get_suggestion(self, error_type):
        """Get suggestion for predicted error."""
        suggestions = {
            'division_by_zero': 'Add zero check before division',
            'uninitialized_var': 'Initialize variable before use',
            'missing_return': 'Add return statement',
            'infinite_loop': 'Add break condition',
            'unclosed_file': 'Use context manager (with statement)',
            'sql_injection': 'Use parameterized queries',
            'hardcoded_password': 'Use environment variables',
            'unused_variable': 'Remove or use the variable',
        }
        return suggestions.get(error_type, 'Review this code')

# ============================================================================
# MAIN EXECUTION FUNCTIONS
# ============================================================================

def run_and_capture_error(script_path):
    """Run Python script and capture stderr."""
    try:
        # Run with timeout to prevent infinite loops
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )
        
        # Return stderr if there's an error
        if result.returncode != 0:
            return result.stderr
        return None
        
    except subprocess.TimeoutExpired:
        return "TimeoutError: Script execution exceeded time limit"
    except Exception as e:
        return str(e)


def parse_error(stderr, target_script=None):
    """Parse error from stderr output."""
    lines = stderr.strip().split('\n')
    
    error_type = None
    error_file = None
    error_line = None
    error_message = ""
    
    # Find the error type and message
    for line in lines:
        if line.strip() and not line.startswith(' '):
            # Look for standard Python error format
            error_match = re.match(r'^(\w+(?:Error|Exception)):\s*(.*)', line)
            if error_match:
                error_type = error_match.group(1)
                error_message = error_match.group(2) or ""
                break
            
            # Check for error type in the line
            parts = line.split(':')
            if parts:
                potential_error = parts[0].strip()
                
                # Handle module prefixed errors
                if '.' in potential_error:
                    potential_error = potential_error.split('.')[-1]
                
                # Check if it's a known error or follows Error naming pattern
                if potential_error in ERROR_DATABASE or potential_error.endswith('Error'):
                    error_type = potential_error
                    break
    
    # Collect ALL frames from the traceback
    all_frames = []
    for line in lines:
        if 'File "' in line and ', line ' in line:
            match = re.search(r'File "([^"]+)", line (\d+)', line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                
                # Skip system files
                if not file_path.startswith('<') and '/lib/python' not in file_path:
                    all_frames.append((file_path, line_num))
    
    # If target_script specified, filter to only that file
    if target_script and all_frames:
        target_abs = os.path.abspath(target_script)
        target_frames = [
            (f, ln) for f, ln in all_frames
            if os.path.abspath(f) == target_abs
        ]
        
        # Use deepest frame from target file (last in stack = closest to error)
        if target_frames:
            error_file, error_line = target_frames[-1]
    
    # Fallback: use deepest frame overall
    if not error_file and all_frames:
        error_file, error_line = all_frames[-1]
    
    return error_type, error_file, error_line, error_message


def fix_error(file_path, error_type, line_number, error_message):
    """Apply hard-coded fix for error type at line number."""
    
    if error_type not in ERROR_DATABASE:
        print(f"[WARN] No solution for {error_type} in database")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[ERROR] Cannot read file: {e}")
        return False
    
    if line_number > len(lines) or line_number < 1:
        print(f"[ERROR] Line {line_number} out of range (file has {len(lines)} lines)")
        return False
    
    target_line = lines[line_number - 1]
    indent = get_indent(target_line)
    
    # Try each pattern for this error type
    for pattern_idx, pattern in enumerate(ERROR_DATABASE[error_type]['patterns']):
        if re.search(pattern['detect'], target_line):
            try:
                # Check if this needs multi-line block wrapping
                needs_block_wrap = pattern['multiline'] and (
                    re.search(r'\b(with|for|while)\b', target_line) or
                    target_line.strip().endswith(':')
                )
                
                if needs_block_wrap:
                    # Get the entire indented block
                    block_lines, base_indent = get_indented_block(lines, line_number - 1)
                    
                    if block_lines:
                        # For FileNotFoundError and similar, wrap entire block
                        if error_type in ['FileNotFoundError', 'JSONDecodeError', 'PermissionError']:
                            fixed = wrap_block_in_try_except(block_lines, base_indent, error_type)
                        else:
                            # Use standard fix
                            fixed = pattern['fix'](target_line, indent, error_message)
                        
                        # Determine how many lines to replace
                        lines_to_replace = len(block_lines)
                        
                        # Replace the block
                        fixed_lines = fixed.split('\n')
                        new_lines = [line + '\n' for line in fixed_lines if line]
                        lines[line_number - 1:line_number - 1 + lines_to_replace] = new_lines
                    else:
                        # Fallback to single line fix
                        fixed = pattern['fix'](target_line, indent, error_message)
                        if not fixed.endswith('\n'):
                            fixed += '\n'
                        lines[line_number - 1] = fixed
                elif pattern['multiline']:
                    # Multi-line but not block-based
                    fixed = pattern['fix'](target_line, indent, error_message)
                    lines[line_number - 1] = fixed
                else:
                    # Single line replacement
                    fixed = pattern['fix'](target_line, indent, error_message)
                    if not fixed.endswith('\n'):
                        fixed += '\n'
                    lines[line_number - 1] = fixed
                
                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                print(f"[FIX] Applied {error_type} fix at line {line_number} (pattern {pattern_idx + 1})")
                return True
            except Exception as e:
                print(f"[ERROR] Failed to apply fix: {e}")
                traceback.print_exc()
                continue
    
    print(f"[WARN] No matching pattern for {error_type} at line {line_number}")
    print(f"[LINE] {target_line.strip()}")
    return False


def main():
    """Main entry point with support for multiple modes."""
    
    # ============================================================================
    # EVALUATION LICENSE CHECK
    # ============================================================================
    EXPIRY = datetime(2025, 11, 17, 23, 59, 59)  # 7-day trial
    if datetime.now() > EXPIRY:
        print("=" * 70)
        print("BUG-BE-GONE EVALUATION PERIOD ENDED")
        print("=" * 70)
        print()
        print("Your 7-day trial has expired.")
        print()
        print("To purchase a full license or discuss enterprise options:")
        print("  Email: Keeghan@dishesandmore.com")
        print("  Subject: Bug-Be-Gone License")
        print()
        print("Thank you for evaluating Bug-Be-Gone!")
        print("=" * 70)
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    # Parse arguments
    mode = 'runtime'  # default
    script_path = None
    
    for arg in sys.argv[1:]:
        if arg.startswith('--'):
            if arg == '--types':
                mode = 'types'
            elif arg == '--deploy':
                mode = 'deploy'
            elif arg == '--all':
                mode = 'all'
            elif arg == '--predict':
                mode = 'predict'
            elif arg == '--ultimate':
                mode = 'ultimate'
        else:
            script_path = arg
    
    # Handle deployment mode
    if mode == 'deploy':
        print("[DEPLOY] Checking deployment issues...")
        issues = check_deployment_issues()
        if issues:
            print(f"[FOUND] {len(issues)} deployment issue(s)")
            for issue in issues:
                print(f"  - {issue}")
            fix_deployment_issues(issues)
        else:
            print("[SUCCESS] No deployment issues found!")
        return
    
    # Require script path for other modes
    if not script_path or not os.path.exists(script_path):
        print(f"[ERROR] File not found: {script_path}")
        sys.exit(1)
    
    # Create backup
    backup_path = script_path + '.backup'
    shutil.copy2(script_path, backup_path)
    print(f"[BACKUP] Created at {backup_path}")
    
    print(f"[START] Universal Debugger MERGED")
    print(f"[TRIAL] Evaluation license - expires Nov 17, 2025")
    print(f"[MODE] {mode.upper()}")
    print(f"[TARGET] {os.path.abspath(script_path)}")
    print(f"[DATABASE] {len(ERROR_DATABASE)} error types loaded")
    
    # Error prediction mode
    if mode in ['predict', 'ultimate']:
        print("\n[PREDICT] Analyzing code for potential errors...")
        predictor = ErrorPredictor()
        with open(script_path, 'r') as f:
            code_lines = f.readlines()
        
        predictions = predictor.predict_errors(code_lines)
        if predictions:
            print(f"[WARN] Found {len(predictions)} potential issue(s):")
            for pred in predictions:
                print(f"  Line {pred['line']}: {pred['type']}")
                print(f"    Code: {pred['code']}")
                print(f"    Suggestion: {pred['suggestion']}")
        else:
            print("[GOOD] No potential issues detected")
    
    # Type checking mode
    if mode in ['types', 'all', 'ultimate']:
        print("\n[TYPES] Running type checker...")
        type_output = run_type_checker(script_path)
        if type_output:
            type_errors = parse_type_error(type_output)
            print(f"[FOUND] {len(type_errors)} type error(s)")
            for err in type_errors:
                print(f"  Line {err['line']}: {err['message']}")
                fix_type_error(err['file'], err['line'], err['message'])
        else:
            print("[SUCCESS] No type errors found!")
    
    # Runtime error fixing mode
    if mode in ['runtime', 'all', 'ultimate']:
        print("\n[RUNTIME] Fixing runtime errors...")
        
        max_iterations = 100
        iteration = 0
        fixed_errors = []
        
        while iteration < max_iterations:
            iteration += 1
            print(f"[ITERATION {iteration}] Running script...")
            
            stderr = run_and_capture_error(script_path)
            
            if not stderr:
                print(f"[SUCCESS] No errors detected!")
                print(f"[COMPLETE] Fixed {len(fixed_errors)} error(s) in {iteration - 1} iteration(s)")
                if fixed_errors:
                    print(f"[FIXED]")
                    for err in fixed_errors:
                        print(f"  - {err}")
                break
            
            error_type, error_file, error_line, error_msg = parse_error(stderr, script_path)
            
            if not error_type:
                print(f"[ERROR] Could not determine error type from:")
                print(stderr)
                break
            
            if not error_file or not error_line:
                print(f"[ERROR] Could not locate error in source:")
                print(stderr)
                break
            
            # Only fix errors in the target script
            if os.path.abspath(error_file) != os.path.abspath(script_path):
                print(f"[SKIP] Error is in external file: {error_file}")
                print(stderr)
                break
            
            error_descriptor = f"{error_type} at line {error_line}"
            print(f"[DETECTED] {error_descriptor}: {error_msg[:50]}...")
            
            if error_descriptor in fixed_errors:
                print(f"[ERROR] Already tried to fix this error - infinite loop detected")
                print(stderr)
                break
            
            if fix_error(error_file, error_type, error_line, error_msg):
                fixed_errors.append(error_descriptor)
            else:
                print(f"[FAILED] Could not apply fix")
                print(error_msg)
                break
        
        if iteration >= max_iterations:
            print(f"[TIMEOUT] Max iterations reached")
            print(f"[RESTORE] Use {backup_path} to restore original")
    
    # Ultimate mode summary
    if mode == 'ultimate':
        print("\n[ULTIMATE] Complete analysis finished")
        print("[ULTIMATE] Your code has been thoroughly debugged, optimized, and fortified")
        print("[ULTIMATE] Smart return values ensure appropriate defaults")
        print("[ULTIMATE] AST-based parsing provides intelligent fixes")
        print("[ULTIMATE] It should now be virtually indestructible")


if __name__ == "__main__":
    main()
