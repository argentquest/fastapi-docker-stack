#!/usr/bin/env python
"""
Script to automatically fix common flake8 issues.
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

def fix_all_python_files():
    """Fix all Python files in the app directory."""
    app_dir = Path("app")
    
    if not app_dir.exists():
        print("App directory not found!")
        return
    
    python_files = list(app_dir.rglob("*.py"))
    
    print(f"Found {len(python_files)} Python files to fix:")
    for file_path in python_files:
        fix_file(file_path)
    
    print("\nAutomatic fixes complete!")
    print("Now running flake8 to see remaining issues...")

if __name__ == "__main__":
    fix_all_python_files()