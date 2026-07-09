import os
import re

for root, _, files in os.walk('/Users/ayush/Desktop/sentinal/backend/app/models'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Replace UUID from postgresql with standard Uuid
            content = re.sub(r'from sqlalchemy\.dialects\.postgresql import (.*?)UUID(.*?)\n', r'from sqlalchemy.dialects.postgresql import \1\2\n', content)
            # If the import becomes empty (e.g., from sqlalchemy.dialects.postgresql import \n), remove it
            content = re.sub(r'from sqlalchemy\.dialects\.postgresql import \s*\n', '', content)
            content = re.sub(r'from sqlalchemy\.dialects\.postgresql import ,\s*', 'from sqlalchemy.dialects.postgresql import ', content)
            content = re.sub(r', \n', '\n', content)
            
            # Add Uuid to sqlalchemy imports
            if 'Uuid' not in content and 'UUID' in content and 'import Uuid' not in content:
                content = re.sub(r'from sqlalchemy import (.*?)\n', r'from sqlalchemy import \1, Uuid as UUID\n', content, count=1)
                
            # Replace INET
            if 'INET' in content:
                content = content.replace('INET,', 'String(45).with_variant(INET(), "postgresql"),')
                content = content.replace('INET\n', 'String(45).with_variant(INET(), "postgresql")\n')
                # Make sure INET is imported
                if 'from sqlalchemy.dialects.postgresql import' in content and 'INET' not in content.split('from sqlalchemy.dialects.postgresql import')[1].split('\n')[0]:
                     content = content.replace('from sqlalchemy.dialects.postgresql import ', 'from sqlalchemy.dialects.postgresql import INET, ')
                elif 'from sqlalchemy.dialects.postgresql import' not in content:
                     content = 'from sqlalchemy.dialects.postgresql import INET\n' + content
                     
            # Replace JSONB
            if 'JSONB' in content:
                content = content.replace('JSONB,', 'JSON().with_variant(JSONB(), "postgresql"),')
                content = content.replace('JSONB\n', 'JSON().with_variant(JSONB(), "postgresql")\n')
                if 'from sqlalchemy import ' in content and 'JSON' not in content:
                     content = content.replace('from sqlalchemy import ', 'from sqlalchemy import JSON, ')
                # Make sure JSONB is imported
                if 'from sqlalchemy.dialects.postgresql import' in content and 'JSONB' not in content.split('from sqlalchemy.dialects.postgresql import')[1].split('\n')[0]:
                     content = content.replace('from sqlalchemy.dialects.postgresql import ', 'from sqlalchemy.dialects.postgresql import JSONB, ')
                elif 'from sqlalchemy.dialects.postgresql import' not in content:
                     content = 'from sqlalchemy.dialects.postgresql import JSONB\n' + content

            with open(filepath, 'w') as f:
                f.write(content)
