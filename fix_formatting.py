import re

# Read the file
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix indentation for validated_bbox lines
content = content.replace('        validated_bbox = validate_bbox(bbox)', '    validated_bbox = validate_bbox(bbox)')

# Fix query formatting - remove unnecessary whitespace in queries
def clean_query(match):
    query_block = match.group(0)
    # Find the triple quotes
    start_idx = query_block.find('"""')
    end_idx = query_block.rfind('"""')
    
    if start_idx == -1 or end_idx == -1 or start_idx == end_idx:
        return query_block
    
    # Get the query content
    query_content = query_block[start_idx+3:end_idx]
    
    # Clean up the query - remove extra indentation
    lines = query_content.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(stripped)
    
    # Rebuild query
    new_query = '\n'.join(cleaned_lines)
    
    return f'query = f"""[out:json][timeout:25];\n{new_query}\n    """'

# Fix all query blocks
content = re.sub(r'query = f""".*?"""', clean_query, content, flags=re.DOTALL)

# Write back
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Formatting fixed!")
