#!/usr/bin/env python
"""
Script to automatically fix common flake8 issues in tests directory.
"""

import os
import re
from pathlib import Path

def fix_file(file_path: Path):
    """Fix common flake8 issues in a single file."""
    print(f"Fixing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix W291: Remove trailing whitespace
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove trailing whitespace (W291)
        line = line.rstrip()
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix W293: Remove whitespace from blank lines
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
    
    # Fix E261: At least two spaces before inline comment
    content = re.sub(r'(\S) #', r'\1  #', content)
    
    # Fix W504: line break after binary operator (move to before)
    content = re.sub(r'(\w+)\s+and\s*\n', r'\n        and \1', content, flags=re.MULTILINE)
    
    # Fix F541: Remove f-string formatting where not needed
    # Replace f"string without placeholders" with "string"
    content = re.sub(r'f"([^"]*)"(?![^"]*\{)', r'"\1"', content)
    content = re.sub(r"f'([^']*)'(?![^']*\{)", r"'\1'", content)
    
    # Ensure file ends with newline (W292)
    if content and not content.endswith('\n'):
        content += '\n'
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Fixed {file_path}")
    else:
        print(f"  No changes needed for {file_path}")

def fix_spacing_issues(file_path: Path):
    """Fix E302 and E305 spacing issues."""
    print(f"Fixing spacing in {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    lines = content.split('\n')
    
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for function definition (E302)
        if re.match(r'^(def |async def |class )', line) and i > 0:
            # Count blank lines before this line
            blank_count = 0
            j = len(fixed_lines) - 1
            while j >= 0 and fixed_lines[j].strip() == '':
                blank_count += 1
                j -= 1
            
            # If less than 2 blank lines, add more
            if blank_count < 2:
                # Remove existing blank lines
                while fixed_lines and fixed_lines[-1].strip() == '':
                    fixed_lines.pop()
                # Add exactly 2 blank lines
                fixed_lines.append('')
                fixed_lines.append('')
        
        fixed_lines.append(line)
        i += 1
    
    # Fix E305 - blank lines after function definitions
    final_lines = []
    for i, line in enumerate(fixed_lines):
        final_lines.append(line)
        
        # If this line ends a function/class and next line is module-level code
        if i < len(fixed_lines) - 1:
            next_line = fixed_lines[i + 1]
            # Check if next line is a module-level statement
            if (line.strip() and not line.startswith(' ') and not line.startswith('\t') 
                and next_line.strip() and not next_line.startswith(' ') and not next_line.startswith('\t')
                and not next_line.startswith('#') and 'if __name__' in next_line):
                
                # Count blank lines after
                blank_count = 0
                j = i + 1
                while j < len(fixed_lines) and fixed_lines[j].strip() == '':
                    blank_count += 1
                    j += 1
                
                if blank_count < 2:
                    # Add blank line
                    final_lines.append('')
    
    new_content = '\n'.join(final_lines)
    
    if new_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Fixed spacing in {file_path}")
    else:
        print(f"  No spacing changes needed for {file_path}")

def fix_all_test_files():
    """Fix all Python files in the tests directory."""
    tests_dir = Path("tests")
    
    if not tests_dir.exists():
        print("Tests directory not found!")
        return
    
    python_files = list(tests_dir.rglob("*.py"))
    
    print(f"Found {len(python_files)} Python test files to fix:")
    
    # First pass: fix basic issues
    for file_path in python_files:
        fix_file(file_path)
    
    print("\nSecond pass: fix spacing issues...")
    # Second pass: fix spacing issues
    for file_path in python_files:
        fix_spacing_issues(file_path)
    
    print("\nAutomatic fixes complete!")
    print("Now running flake8 to see remaining issues...")

if __name__ == "__main__":
    fix_all_test_files()