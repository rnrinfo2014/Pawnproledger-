"""
Script to fix SQLAlchemy type checking issues by adding type ignore comments
"""

import re

def fix_sqlalchemy_type_issues():
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match db.query() calls
    patterns = [
        r'(db\.query\([^)]+\)\.filter\([^)]+\)\.first\(\))',
        r'(db\.query\([^)]+\)\.offset\([^)]+\)\.limit\([^)]+\)\.all\(\))',
        r'(db\.query\([^)]+\)\.all\(\))',
        r'(db\.query\([^)]+\)\.first\(\))',
        r'(db\.query\([^)]+\)\.count\(\))',
        r'(query\.filter\([^)]+\))',
    ]
    
    for pattern in patterns:
        content = re.sub(pattern, r'\1  # type: ignore', content)
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added type ignore comments to SQLAlchemy queries")

if __name__ == "__main__":
    fix_sqlalchemy_type_issues()