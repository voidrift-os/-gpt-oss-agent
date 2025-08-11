#!/usr/bin/env python3
"""
Fix markdown linting issues in a file with repeated sections.
"""
import re
import sys

def fix_markdown_linting(content: str) -> str:
    """Fix MD024 (duplicate headings) and MD040 (fenced code language) issues."""
    
    lines = content.split('\n')
    fixed_lines = []
    step_counter = 1
    
    for i, line in enumerate(lines):
        # Fix duplicate "License: Apache-2.0" headings by adding step numbers
        if line.strip() == "## License: Apache-2.0":
            fixed_lines.append(f"## License: Apache-2.0 (Step {step_counter})")
            step_counter += 1
        # Fix fenced code blocks without language specification
        elif line.strip() == "```" and i + 1 < len(lines):
            # Look ahead to see what type of content follows
            next_non_empty = ""
            for j in range(i + 1, min(i + 5, len(lines))):
                if lines[j].strip():
                    next_non_empty = lines[j].strip()
                    break
            
            # Determine language based on content
            if any(keyword in next_non_empty.lower() for keyword in ['on:', 'runs-on:', 'steps:', 'uses:', 'name:']):
                fixed_lines.append("```yaml")
            elif next_non_empty.startswith(('#!/', 'python', 'import', 'def ', 'class ')):
                fixed_lines.append("```python")
            elif next_non_empty.startswith(('#!/bin/bash', 'echo', 'cd ', 'ls ', 'mkdir')):
                fixed_lines.append("```bash")
            else:
                # Default to yaml since this appears to be GitHub Actions content
                fixed_lines.append("```yaml")
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python fix_markdown.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content = fix_markdown_linting(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"Fixed markdown linting issues in {file_path}")
        
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
