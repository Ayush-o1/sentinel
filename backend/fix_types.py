import os
import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    if '| None' not in content:
        return
        
    print(f"Fixing {filepath}")
    
    # We will do simple string replacements for the known ones
    content = content.replace("uuid.UUID | None", "Optional[uuid.UUID]")
    content = content.replace("str | None", "Optional[str]")
    content = content.replace("dict[str, Any] | None", "Optional[dict[str, Any]]")
    content = content.replace("datetime | None", "Optional[datetime]")
    content = content.replace("HTTPAuthorizationCredentials | None", "Optional[HTTPAuthorizationCredentials]")
    content = content.replace('"ModelVersion | None"', 'Optional["ModelVersion"]')
    
    # Add Optional import if missing
    if "from typing import " in content and "Optional" not in content:
        content = content.replace("from typing import ", "from typing import Optional, ")
    elif "from typing import" not in content:
        # Just put it after other imports
        content = re.sub(r'^(import .*|from .* import .*)$', r'\1\nfrom typing import Optional', content, count=1, flags=re.MULTILINE)
        
    with open(filepath, 'w') as f:
        f.write(content)

for root, _, files in os.walk('/Users/ayush/Desktop/sentinal/backend/app'):
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))
