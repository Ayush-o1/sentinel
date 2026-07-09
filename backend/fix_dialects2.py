import os
import re

for root, _, files in os.walk('/Users/ayush/Desktop/sentinal/backend/app/models'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Undo the bad lines
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('from sqlalchemy.dialects.postgresql import String(45)'):
                    # We broke it here.
                    new_lines.append('from sqlalchemy.dialects.postgresql import INET, JSONB')
                else:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            # Fix usages:
            # For INET, replace `Mapped[Optional[str]] = mapped_column(String(45).with_variant(INET(), "postgresql"),`
            # with standard `Mapped[Optional[str]] = mapped_column(String(45).with_variant(INET(), "postgresql"),`
            # Wait, the script replaced `INET,` with `String(45).with_variant(INET(), "postgresql"),`. This is actually valid Python *except* in the import statement!
            
            # Let's fix the import statement by removing String(45).with_variant(...)
            content = re.sub(r'from sqlalchemy\.dialects\.postgresql import.*?JSON\(\)\.with_variant\(JSONB\(\), "postgresql"\).*?', 'from sqlalchemy.dialects.postgresql import INET, JSONB', content)
            
            # Make sure we import String, JSON
            if 'from sqlalchemy import ' in content and 'String' not in content:
                 content = content.replace('from sqlalchemy import ', 'from sqlalchemy import String, ')
            if 'from sqlalchemy import ' in content and 'JSON' not in content:
                 content = content.replace('from sqlalchemy import ', 'from sqlalchemy import JSON, ')
                 
            with open(filepath, 'w') as f:
                f.write(content)

