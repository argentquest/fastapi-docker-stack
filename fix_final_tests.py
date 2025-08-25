#!/usr/bin/env python
"""
Script to fix the final remaining flake8 issues in tests directory.
"""

import os
import re
from pathlib import Path


def fix_e305_specific():
    """Fix E305 issues by adding blank lines before 'if __name__' statements."""
    files_to_fix = [
        "tests/quick_test.py",
        "tests/test_01_containers_health.py", 
        "tests/test_03_openrouter_integration.py",
        "tests/test_04_minio_storage.py",
        "tests/test_05_redis_cache.py",
        "tests/test_06_end_to_end.py"
    ]
    
    for file_path in files_to_fix:
        file_path = Path(file_path)
        if not file_path.exists():
            continue
            
        print(f"Fixing E305 in {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Find if __name__ == '__main__' or if __name__ == "__main__"
        # and ensure it has 2 blank lines before it
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check if this line is 'if __name__' 
            if line.strip().startswith('if __name__'):
                # Count how many blank lines are before this line
                blank_lines = 0
                j = i - 1
                while j >= 0 and lines[j].strip() == '':
                    blank_lines += 1
                    j -= 1
                
                # If we have fewer than 2 blank lines, add more
                if blank_lines < 2:
                    # Remove existing blank lines from fixed_lines
                    while fixed_lines and fixed_lines[-1].strip() == '':
                        fixed_lines.pop()
                    # Add exactly 2 blank lines
                    fixed_lines.append('')
                    fixed_lines.append('')
            
            fixed_lines.append(line)
        
        new_content = '\n'.join(fixed_lines)
        
        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  Fixed E305 in {file_path}")
        else:
            print(f"  No E305 changes needed for {file_path}")


def fix_e271_issue():
    """Fix E271 - multiple spaces after keyword in test_both_ports.py."""
    file_path = Path("tests/test_both_ports.py")
    
    if not file_path.exists():
        return
    
    print(f"Fixing E271 in {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix multiple spaces after 'and' keyword
    content = re.sub(
        r'and\s+debug_health',
        'and debug_health',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Fixed E271 in {file_path}")
    else:
        print(f"  No E271 changes needed for {file_path}")


def main():
    """Run all fixes."""
    print("Fixing final remaining flake8 issues...")
    
    fix_e305_specific()
    fix_e271_issue()
    
    print("\nAll final fixes applied!")


if __name__ == "__main__":
    main()