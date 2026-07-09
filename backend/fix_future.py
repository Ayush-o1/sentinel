import os

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    if 'from __future__ import annotations' not in content:
        # Find the first non-comment, non-docstring line
        lines = content.split('\n')
        out_lines = []
        inserted = False
        in_docstring = False
        for line in lines:
            if not inserted:
                # Basic docstring check
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    if not in_docstring:
                        in_docstring = True
                        if line.strip().count('"""') == 2 or line.strip().count("'''") == 2:
                            in_docstring = False # single line docstring
                    else:
                        in_docstring = False
                elif not in_docstring and not line.strip().startswith('#') and line.strip() != '':
                    out_lines.append('from __future__ import annotations')
                    inserted = True
            out_lines.append(line)
        
        if not inserted:
            out_lines.insert(0, 'from __future__ import annotations')
            
        with open(filepath, 'w') as f:
            f.write('\n'.join(out_lines))

for root, _, files in os.walk('/Users/ayush/Desktop/sentinal/backend/app'):
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))

for root, _, files in os.walk('/Users/ayush/Desktop/sentinal/backend/tests'):
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))
