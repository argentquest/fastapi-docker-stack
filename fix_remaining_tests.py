#!/usr/bin/env python
"""
Script to fix the remaining 8 flake8 issues in tests directory.
"""

import os
import re
from pathlib import Path


def fix_e305_issues():
    """Fix E305 - expected 2 blank lines after class or function definition."""
    files_to_fix = [
        "tests/config.py",
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
        lines = content.split('\n')
        
        # Look for 'if __name__' or module-level assignments after function definitions
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)
            
            # Check if this line ends a function/class and next line is module-level
            if (i < len(lines) - 1 and 
                line.strip() and not line.startswith(' ') and not line.startswith('\t')):
                
                next_line = lines[i + 1]
                
                # If next line is if __name__ or module-level assignment
                if (next_line.strip() and 
                    (next_line.startswith('if __name__') or 
                     (not next_line.startswith(' ') and not next_line.startswith('\t') and 
                      not next_line.startswith('#') and '=' in next_line))):
                    
                    # Check if there are already 2 blank lines
                    blank_count = 0
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == '':
                        blank_count += 1
                        j += 1
                    
                    if blank_count < 2:
                        # Add the missing blank line(s)
                        for _ in range(2 - blank_count):
                            fixed_lines.append('')
            
            i += 1
        
        new_content = '\n'.join(fixed_lines)
        
        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  Fixed E305 in {file_path}")
        else:
            print(f"  No E305 changes needed for {file_path}")


def fix_w504_issue():
    """Fix W504 - line break after binary operator in test_both_ports.py."""
    file_path = Path("tests/test_both_ports.py")
    
    if not file_path.exists():
        return
    
    print(f"Fixing W504 in {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix the specific W504 issue: move 'and' to beginning of next line
    content = re.sub(
        r'docker_health\.get\("status"\) == "accessible" and\s*\n',
        'docker_health.get("status") == "accessible"\n        and ',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Fixed W504 in {file_path}")
    else:
        print(f"  No W504 changes needed for {file_path}")


def main():
    """Run all fixes."""
    print("Fixing remaining flake8 issues in tests directory...")
    
    fix_e305_issues()
    fix_w504_issue()
    
    print("\nAll remaining fixes applied!")


if __name__ == "__main__":
    main()