#!/usr/bin/env python3
"""
PawnSoft API to Markdown Generator
Extracts API endpoints from OpenAPI spec and saves to markdown file
"""
import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = 'http://localhost:8000'

def get_api_endpoints():
    """Get all API endpoints from FastAPI's OpenAPI specification"""
    try:
        response = requests.get(f'{BASE_URL}/openapi.json')
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get OpenAPI spec: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return None

def format_endpoints_by_module(openapi_data: Dict[str, Any]):
    """Format endpoints organized by module/tag"""
    
    if not openapi_data or 'paths' not in openapi_data:
        return {}
    
    paths = openapi_data['paths']
    endpoints_by_tag = {}
    
    for path, path_data in paths.items():
        for method, method_data in path_data.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                tags = method_data.get('tags', ['Untagged'])
                summary = method_data.get('summary', 'No description')
                operation_id = method_data.get('operationId', '')
                description = method_data.get('description', '')
                
                for tag in tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    
                    endpoints_by_tag[tag].append({
                        'method': method.upper(),
                        'path': path,
                        'summary': summary,
                        'description': description,
                        'operation_id': operation_id,
                        'parameters': method_data.get('parameters', []),
                        'request_body': method_data.get('requestBody', {}),
                        'responses': method_data.get('responses', {})
                    })
    
    return endpoints_by_tag

def get_method_emoji(method):
    """Get emoji for HTTP method"""
    emojis = {
        'GET': '🟢',
        'POST': '🔵', 
        'PUT': '🟡',
        'DELETE': '🔴',
        'PATCH': '🟠'
    }
    return emojis.get(method, '⚪')

def generate_markdown_documentation():
    """Generate comprehensive markdown documentation"""
    
    print("🔍 Fetching API endpoints...")
    openapi_data = get_api_endpoints()
    if not openapi_data:
        print("❌ Could not retrieve API endpoints")
        return None
    
    endpoints_by_tag = format_endpoints_by_module(openapi_data)
    if not endpoints_by_tag:
        print("❌ No endpoints found")
        return None
    
    # Calculate statistics
    total_endpoints = sum(len(endpoints) for endpoints in endpoints_by_tag.values())
    method_counts = {'GET': 0, 'POST': 0, 'PUT': 0, 'DELETE': 0, 'PATCH': 0}
    
    for tag, endpoints in endpoints_by_tag.items():
        for endpoint in endpoints:
            method = endpoint['method']
            if method in method_counts:
                method_counts[method] += 1
    
    # Generate markdown content
    timestamp = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    
    markdown_content = f"""# PawnSoft API Complete Documentation

**Generated:** {timestamp}  
**Total Endpoints:** {total_endpoints}  
**Base URL:** {BASE_URL}

---

## 📊 Quick Statistics

| Metric | Count |
|--------|-------|
| Total Endpoints | {total_endpoints} |
| Modules | {len(endpoints_by_tag)} |
| GET Methods | {method_counts['GET']} |
| POST Methods | {method_counts['POST']} |
| PUT Methods | {method_counts['PUT']} |
| DELETE Methods | {method_counts['DELETE']} |

## 🔗 API Access

- **Swagger UI:** [{BASE_URL}/docs]({BASE_URL}/docs)
- **ReDoc:** [{BASE_URL}/redoc]({BASE_URL}/redoc)  
- **OpenAPI JSON:** [{BASE_URL}/openapi.json]({BASE_URL}/openapi.json)

---

"""

    # Module order
    module_order = [
        'Pledge Payments', 'Payment Management', 'Customer Ledger Reports', 
        'Payment Receipts', 'Chart of Accounts', 'Daybook', 'Untagged'
    ]
    
    # Process each module
    for module in module_order:
        if module in endpoints_by_tag:
            endpoints = endpoints_by_tag[module]
            
            markdown_content += f"\n## 📂 {module} ({len(endpoints)} endpoints)\n\n"
            
            # Add module description
            module_descriptions = {
                'Pledge Payments': 'Handle multiple pledge payments and pending pledge calculations',
                'Payment Management': 'Advanced payment receipt management with transaction reversal',
                'Customer Ledger Reports': 'Comprehensive customer financial reporting and ledger management',
                'Payment Receipts': 'Receipt management, search, and retrieval system',
                'Chart of Accounts': 'Financial accounting structure and account management',
                'Daybook': 'Daily transaction summaries and financial reporting',
                'Untagged': 'Core business operations and entity management'
            }
            
            if module in module_descriptions:
                markdown_content += f"*{module_descriptions[module]}*\n\n"
            
            # Create table header
            markdown_content += "| # | Method | Endpoint | Description |\n"
            markdown_content += "|---|--------|----------|-------------|\n"
            
            # Add endpoints
            for i, endpoint in enumerate(endpoints, 1):
                method = endpoint['method']
                path = endpoint['path']
                summary = endpoint['summary']
                emoji = get_method_emoji(method)
                
                # Escape pipe characters in descriptions
                summary = summary.replace('|', '\\|')
                
                markdown_content += f"| {i} | {emoji} {method} | `{path}` | {summary} |\n"
            
            # Add detailed information for key modules
            if module in ['Pledge Payments', 'Payment Management', 'Customer Ledger Reports']:
                markdown_content += f"\n### Key Features:\n"
                
                key_features = {
                    'Pledge Payments': [
                        "Fetch customer's pending pledges with detailed calculations",
                        "Process multiple pledge payments in single transaction", 
                        "Automatic interest calculation and balance updates",
                        "Receipt generation for multiple pledges"
                    ],
                    'Payment Management': [
                        "Update payment receipts with automatic transaction reversal",
                        "Delete payments with complete accounting integrity",
                        "Safety restrictions (age limits, admin access)",
                        "Comprehensive audit trails",
                        "Automatic pledge status recalculation"
                    ],
                    'Customer Ledger Reports': [
                        "Date-wise customer statements",
                        "Financial year summaries", 
                        "Current balance calculations",
                        "All customers overview with filtering"
                    ]
                }
                
                if module in key_features:
                    for feature in key_features[module]:
                        markdown_content += f"- {feature}\n"
            
            markdown_content += "\n---\n"
    
    # Add remaining modules
    for tag, endpoints in endpoints_by_tag.items():
        if tag not in module_order and endpoints:
            markdown_content += f"\n## 📂 {tag} ({len(endpoints)} endpoints)\n\n"
            
            markdown_content += "| # | Method | Endpoint | Description |\n"
            markdown_content += "|---|--------|----------|-------------|\n"
            
            for i, endpoint in enumerate(endpoints, 1):
                method = endpoint['method']
                path = endpoint['path']
                summary = endpoint['summary']
                emoji = get_method_emoji(method)
                
                summary = summary.replace('|', '\\|')
                markdown_content += f"| {i} | {emoji} {method} | `{path}` | {summary} |\n"
            
            markdown_content += "\n---\n"
    
    # Add common workflows section
    markdown_content += """
## 🚀 Common API Workflows

### Authentication Flow
```bash
# 1. Login to get access token
curl -X POST "{BASE_URL}/token" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=admin&password=password"

# 2. Use token in subsequent requests
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  "{BASE_URL}/users/me"
```

### Customer & Pledge Management
```bash
# 1. Create customer
POST /customers

# 2. Create pledge with items  
POST /pledges/with-items

# 3. Get customer pending pledges
GET /api/v1/pledge-payments/customers/{{customer_id}}/pending

# 4. Process multiple payments
POST /api/v1/pledge-payments/customers/{{customer_id}}/multiple-payment
```

### Payment Management
```bash
# 1. Check if payment can be modified
GET /api/v1/payment-management/payment/{{payment_id}}/can-modify

# 2. Update payment (with transaction reversal)
PUT /api/v1/payment-management/payment/{{payment_id}}

# 3. Delete payment (with accounting integrity)  
DELETE /api/v1/payment-management/payment/{{payment_id}}
```

### Reporting & Analysis
```bash
# 1. Customer ledger statement
GET /api/v1/customer-ledger/customer/{{customer_id}}/statement

# 2. Daily transaction summary
GET /api/v1/daybook/daily-summary

# 3. Receipt details
GET /api/v1/receipts/receipt/{{receipt_no}}
```

---

## 📋 Response Format

All API responses follow this standard format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2025-10-18T18:35:16Z"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [...]
  },
  "timestamp": "2025-10-18T18:35:16Z"
}
```

---

## 🔐 Authentication

Most endpoints require authentication. Include the JWT token in requests:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

**Token Endpoints:**
- `POST /token` - Get access token with username/password

---

## 📖 Additional Resources

- **Interactive API Testing:** Visit [{BASE_URL}/docs]({BASE_URL}/docs) for Swagger UI
- **API Schema:** Download from [{BASE_URL}/openapi.json]({BASE_URL}/openapi.json)
- **Support:** Contact development team for API assistance

---

*Documentation generated automatically from OpenAPI specification*  
*Last updated: {timestamp}*
""".replace('{BASE_URL}', BASE_URL)
    
    # Save to file
    filename = f"COMPLETE_API_DOCUMENTATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return filename

if __name__ == '__main__':
    print("🚀 PawnSoft API to Markdown Generator")
    print("=" * 50)
    
    # Check server
    try:
        response = requests.get(f'{BASE_URL}/docs', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️  Server responded but may have issues")
    except:
        print("❌ Server not running. Start with: python run_server.py")
        exit(1)
    
    # Generate documentation
    filename = generate_markdown_documentation()
    
    if filename:
        print(f"\n🎉 SUCCESS! Markdown documentation generated:")
        print(f"📄 File: {filename}")
        print(f"📁 Location: {os.path.abspath(filename) if 'os' in globals() else filename}")
        print(f"📊 Size: {len(open(filename, 'r', encoding='utf-8').read())} characters")
    else:
        print("❌ Failed to generate documentation")
    
    print("\n" + "=" * 50)
    print("📚 API DOCUMENTATION COMPLETE!")