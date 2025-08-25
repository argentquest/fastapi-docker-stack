#!/usr/bin/env python
"""
Script to fix E302 and E305 spacing issues.
"""

import re
from pathlib import Path

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
        
        # Check for class definition (E302)
        if re.match(r'^class \w+', line) and i > 0:
            # Count blank lines before this line
            blank_count = 0
            j = i - 1
            while j >= 0 and lines[j].strip() == '':
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
        
        # Check for function definition (E302)
        elif re.match(r'^@\w+|^def \w+|^async def \w+', line) and i > 0:
            # Don't add blank lines after @decorator
            if not re.match(r'^@\w+', line):
                # Count blank lines before this line
                blank_count = 0
                j = i - 1
                while j >= 0 and lines[j].strip() == '':
                    blank_count += 1
                    j -= 1
                
                # Skip if previous line is a decorator
                if j >= 0 and re.match(r'^@\w+', lines[j]):
                    pass  # Don't add blank lines after decorators
                elif blank_count < 2:
                    # Remove existing blank lines
                    while fixed_lines and fixed_lines[-1].strip() == '':
                        fixed_lines.pop()
                    # Add exactly 2 blank lines
                    fixed_lines.append('')
                    fixed_lines.append('')
        
        fixed_lines.append(line)
        i += 1
    
    # Fix E305 - blank lines after class/function definitions
    final_lines = []
    for i, line in enumerate(fixed_lines):
        final_lines.append(line)
        
        # If this line is a class or function end, ensure proper spacing after
        if i < len(fixed_lines) - 1:
            next_line = fixed_lines[i + 1]
            # Check if next line is a module-level statement (not indented)
            if (line.strip() and not line.startswith(' ') and not line.startswith('\t') 
                and next_line.strip() and not next_line.startswith(' ') and not next_line.startswith('\t')
                and not next_line.startswith('#') and '=' in next_line):
                
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

def main():
    """Fix spacing in all Python files."""
    app_dir = Path("app")
    python_files = list(app_dir.rglob("*.py"))
    
    for file_path in python_files:
        fix_spacing_issues(file_path)
    
    print("Spacing fixes complete!")

if __name__ == "__main__":
    main()