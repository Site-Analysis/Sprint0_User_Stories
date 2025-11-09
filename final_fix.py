import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove duplicate [out:json][timeout:25]; lines
content = re.sub(r'\[out:json\]\[timeout:25\];\s*\[out:json\]\[timeout:25\];', '[out:json][timeout:25];', content)

# Fix all query blocks to be single-line format (this avoids whitespace issues)
def fix_multiline_query(match):
    full_match = match.group(0)
    # Extract just the query content between triple quotes
    start = full_match.find('"""') + 3
    end = full_match.rfind('"""')
    query_content = full_match[start:end]
    
    # Remove ALL whitespace and newlines, then rejoin
    query_clean = ' '.join(query_content.split())
    
    # Return properly formatted
    return f'query = f"""{query_clean}"""'

# Apply to all query blocks
content = re.sub(r'query = f""".*?"""', fix_multiline_query, content, flags=re.DOTALL)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("All queries fixed!")
