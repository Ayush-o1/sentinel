import os

for root, _, files in os.walk('/Users/ayush/Desktop/sentinal/backend/app'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            if 'Optional' in content and 'from typing import ' not in content:
                content = 'from typing import Optional\n' + content
                with open(filepath, 'w') as f:
                    f.write(content)
            elif 'Optional' in content and 'from typing import ' in content and 'Optional' not in content:
                content = content.replace('from typing import ', 'from typing import Optional, ')
                with open(filepath, 'w') as f:
                    f.write(content)
