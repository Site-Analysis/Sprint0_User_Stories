import re

# Read the file
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add validate_bbox to all endpoints that don't have it
# Pattern 1: Find all functions and add validation
functions_with_bbox = re.findall(r'async def (\w+)\([^)]*bbox: str[^)]*\):', content)

# Pattern 2: Replace query patterns to remove extra whitespace and validate bbox
def fix_query(match):
    full_match = match.group(0)
    # Remove leading whitespace from query lines
    lines = full_match.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        if i == 0:
            # First line - keep as is but ensure no leading spaces after """
            fixed_lines.append(line.replace('    [out:json]', '[out:json]'))
        elif '"""' in line:
            # Last line
            fixed_lines.append(line)
        else:
            # Middle lines - remove leading spaces
            fixed_lines.append(line.lstrip())
    return '\n'.join(fixed_lines)

# Fix all query definitions
content = re.sub(r'query = f"""[^"]*"""', fix_query, content, flags=re.DOTALL)

# Now add validated_bbox = validate_bbox(bbox) before each query = f""" line
# Find all functions with bbox parameter and add validation

def add_validation(match):
    func_content = match.group(0)
    # Check if validation already exists
    if 'validated_bbox = validate_bbox(bbox)' in func_content:
        return func_content
    
    # Find the position to insert validation (before query = f""")
    query_pos = func_content.find('query = f"""')
    if query_pos == -1:
        return func_content
    
    # Insert validation line
    # Find the proper indentation
    lines_before = func_content[:query_pos].split('\n')
    last_line = lines_before[-1] if lines_before else ''
    indent = len(last_line) - len(last_line.lstrip())
    
    validation_line = ' ' * indent + 'validated_bbox = validate_bbox(bbox)\n' + ' ' * indent
    new_content = func_content[:query_pos] + validation_line + func_content[query_pos:]
    
    # Also replace ({bbox}) with ({validated_bbox}) in queries
    new_content = new_content.replace('({bbox})', '({validated_bbox})')
    
    return new_content

# Apply to all async functions with bbox parameter
pattern = r'async def [^:]+bbox: str[^:]+:.*?(?=\n@app\.|$)'
content = re.sub(pattern, add_validation, content, flags=re.DOTALL)

# Write the fixed content
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all queries in main.py")
