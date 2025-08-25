#!/usr/bin/env python
"""
Manual fix for the remaining spacing issues.
"""

import re
from pathlib import Path

def fix_remaining_issues():
    """Fix the specific remaining issues."""
    
    # Fix service files - add blank lines before module-level assignments
    service_files = [
        "app/services/cache_service.py",
        "app/services/database_service.py", 
        "app/services/embedding_service.py",
        "app/services/openrouter_service.py",
        "app/services/storage_service.py"
    ]
    
    for file_path in service_files:
        path = Path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add blank lines before the service instance creation
        service_name = path.stem  # e.g., "cache_service"
        pattern = f"^{service_name} = "
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.match(pattern, line) and i > 0:
                # Count blank lines before
                blank_count = 0
                j = i - 1
                while j >= 0 and lines[j].strip() == '':
                    blank_count += 1
                    j -= 1
                
                if blank_count < 2:
                    # Insert additional blank lines
                    for _ in range(2 - blank_count):
                        lines.insert(i, '')
                break
        
        new_content = '\n'.join(lines)
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed {file_path}")
    
    # Fix main.py files - add blank lines before decorators
    main_files = ["app/main.py", "app/main_fixed.py"]
    
    for file_path in main_files:
        path = Path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for decorator
            if re.match(r'^@(app\.|asynccontextmanager)', line) and i > 0:
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
        
        new_content = '\n'.join(fixed_lines)
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_remaining_issues()
    print("Manual fixes complete!")