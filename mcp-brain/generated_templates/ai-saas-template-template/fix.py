import glob
import os
import re

count = 0
for file in glob.glob('src/components/*.jsx'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Strip leading whitespace and \ characters
    cleaned = re.sub(r'^[\s\\]+', '', content)
    
    if len(cleaned) < len(content):
        with open(file, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        count += 1
        print(f'Fixed {file}')

print(f'Done fixing {count} files.')
