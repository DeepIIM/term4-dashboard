"""
Builds the final index.html by replacing the DEFAULT_DATA JSON in the existing index.html template.
This preserves all UI features (setup wizard, clash tracker, CFA timer, etc.) while updating the course data.
"""

import json
import re

# Load updated courses.json (with sister sections)
with open('courses.json', 'r', encoding='utf-8') as f:
    courses_data = json.load(f)

# Read existing index.html as template
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace DEFAULT_DATA JSON
pattern = r'(const DEFAULT_DATA = )(\{.*?\})(;\s*\n\s*let data = DEFAULT_DATA)'

def replacer(m):
    prefix = m.group(1)
    suffix = m.group(3)
    new_json = json.dumps(courses_data, ensure_ascii=False)
    return prefix + new_json + suffix

new_html = re.sub(pattern, replacer, html, count=1, flags=re.DOTALL)

# Check if replacement actually happened
match = re.search(pattern, html, flags=re.DOTALL)
if not match:
    print("WARNING: Could not find DEFAULT_DATA to replace. index.html may be out of sync.")
else:
    old_data = match.group(2)
    new_json = json.dumps(courses_data, ensure_ascii=False)
    if old_data == new_json:
        print("index.html is already up to date. No changes needed.")
    else:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f"Built index.html successfully")
    print(f"File size: {len(new_html):,} bytes")
