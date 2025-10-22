#!/usr/bin/env python3
"""
PawnSoft API Endpoints Documentation Generator
Generates a complete list of all available API endpoints in the application
"""
import requests
import json
from typing import Dict, List, Any

BASE_URL = 'http://localhost:8000'

def get_api_endpoints():
    """Get all API endpoints from FastAPI's OpenAPI specification"""
    try:
        # Get OpenAPI schema
        response = requests.get(f'{BASE_URL}/openapi.json')
        if response.status_code == 200:
            openapi_data = response.json()
            return openapi_data
        else:
            print(f"❌ Failed to get OpenAPI spec: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return None

def format_endpoints_by_module(openapi_data: Dict[str, Any]):
    """Format endpoints organized by module/tag"""
    
    if not openapi_data or 'paths' not in openapi_data:
        print("❌ No API paths found")
        return
    
    paths = openapi_data['paths']
    tags_info = openapi_data.get('tags', [])
    
    # Group endpoints by tags
    endpoints_by_tag = {}
    
    for path, path_data in paths.items():
        for method, method_data in path_data.items():
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                tags = method_data.get('tags', ['Untagged'])
                summary = method_data.get('summary', 'No description')
                operation_id = method_data.get('operationId', '')
                
                for tag in tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    
                    endpoints_by_tag[tag].append({
                        'method': method.upper(),
                        'path': path,
                        'summary': summary,
                        'operation_id': operation_id,
                        'parameters': method_data.get('parameters', []),
                        'request_body': method_data.get('requestBody', {}),
                        'responses': method_data.get('responses', {})
                    })
    
    return endpoints_by_tag

def print_comprehensive_api_list():
    """Print a comprehensive, organized list of all API endpoints"""
    
    print("🚀 PAWNSOFT API ENDPOINTS - COMPLETE LIST")
    print("=" * 80)
    
    # Get API data
    openapi_data = get_api_endpoints()
    if not openapi_data:
        print("❌ Could not retrieve API endpoints. Make sure the server is running.")
        return
    
    endpoints_by_tag = format_endpoints_by_module(openapi_data)
    
    if not endpoints_by_tag:
        print("❌ No endpoints found")
        return
    
    total_endpoints = sum(len(endpoints) for endpoints in endpoints_by_tag.values())
    
    print(f"📊 TOTAL API ENDPOINTS: {total_endpoints}")
    print(f"📁 TOTAL MODULES: {len(endpoints_by_tag)}")
    print("=" * 80)
    
    # Module order for better organization
    module_order = [
        'Authentication',
        'Users',
        'Companies', 
        'Customers',
        'Pledges',
        'Pledge Payments',
        'Payment Management',
        'Customer Ledger Reports',
        'Receipts',
        'Chart of Accounts',
        'Daybook',
        'Areas',
        'Gold/Silver Rates',
        'Jewell Types',
        'Jewell Rates',
        'Jewell Designs',
        'Jewell Conditions',
        'Schemes',
        'Banks',
        'Items',
        'default'
    ]
    
    # Print endpoints by module
    for module in module_order:
        if module in endpoints_by_tag:
            endpoints = endpoints_by_tag[module]
            print(f"\n📂 {module.upper()} ({len(endpoints)} endpoints)")
            print("-" * 60)
            
            for i, endpoint in enumerate(endpoints, 1):
                method = endpoint['method']
                path = endpoint['path']
                summary = endpoint['summary']
                
                # Color coding by method
                method_color = {
                    'GET': '🟢', 'POST': '🔵', 'PUT': '🟡', 'DELETE': '🔴', 'PATCH': '🟠'
                }.get(method, '⚪')
                
                print(f"   {i:2d}. {method_color} {method:<7} {path:<40} {summary}")
                
                # Show parameters if any
                params = endpoint.get('parameters', [])
                if params:
                    query_params = [p for p in params if p.get('in') == 'query']
                    path_params = [p for p in params if p.get('in') == 'path']
                    
                    if path_params:
                        path_param_names = [p.get('name') for p in path_params]
                        print(f"       🔗 Path params: {', '.join(path_param_names)}")
                    
                    if query_params:
                        query_param_names = [p.get('name') for p in query_params[:3]]  # Show first 3
                        more_params = len(query_params) - 3
                        params_str = ', '.join(query_param_names)
                        if more_params > 0:
                            params_str += f" (+{more_params} more)"
                        print(f"       ❓ Query params: {params_str}")
                
                # Show request body info
                if endpoint.get('request_body'):
                    print(f"       📝 Requires request body")
        
        # Remove processed module
        if module in endpoints_by_tag:
            del endpoints_by_tag[module]
    
    # Print any remaining unorganized endpoints
    for tag, endpoints in endpoints_by_tag.items():
        if endpoints:
            print(f"\n📂 {tag.upper()} ({len(endpoints)} endpoints)")
            print("-" * 60)
            
            for i, endpoint in enumerate(endpoints, 1):
                method = endpoint['method']
                path = endpoint['path']
                summary = endpoint['summary']
                
                method_color = {
                    'GET': '🟢', 'POST': '🔵', 'PUT': '🟡', 'DELETE': '🔴', 'PATCH': '🟠'
                }.get(method, '⚪')
                
                print(f"   {i:2d}. {method_color} {method:<7} {path:<40} {summary}")

def print_endpoint_summary_stats():
    """Print summary statistics about the API"""
    
    print(f"\n📈 API STATISTICS")
    print("-" * 40)
    
    openapi_data = get_api_endpoints()
    if not openapi_data:
        return
    
    endpoints_by_tag = format_endpoints_by_module(openapi_data)
    
    # Count by method
    method_counts = {'GET': 0, 'POST': 0, 'PUT': 0, 'DELETE': 0, 'PATCH': 0}
    
    for tag, endpoints in endpoints_by_tag.items():
        for endpoint in endpoints:
            method = endpoint['method']
            if method in method_counts:
                method_counts[method] += 1
    
    print("Method Distribution:")
    for method, count in method_counts.items():
        if count > 0:
            print(f"   {method:<7}: {count:2d} endpoints")
    
    print(f"\nModule Distribution:")
    sorted_modules = sorted(endpoints_by_tag.items(), key=lambda x: len(x[1]), reverse=True)
    for tag, endpoints in sorted_modules[:10]:  # Top 10 modules
        print(f"   {tag:<25}: {len(endpoints):2d} endpoints")
    
    # API Base URLs
    print(f"\n🔗 API Access:")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Swagger UI: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")
    print(f"   OpenAPI JSON: {BASE_URL}/openapi.json")

def print_key_business_endpoints():
    """Print the most important business endpoints"""
    
    print(f"\n⭐ KEY BUSINESS ENDPOINTS")
    print("-" * 50)
    
    key_endpoints = [
        ("Authentication", "POST", "/token", "Login for access token"),
        ("Customers", "GET", "/customers", "List all customers"),
        ("Pledges", "POST", "/pledges", "Create new pledge"),
        ("Pledge Payments", "POST", "/api/v1/pledge-payments/customers/{customer_id}/multiple-payment", "Multiple pledge payment"),
        ("Pledge Payments", "GET", "/api/v1/pledge-payments/customers/{customer_id}/pending", "Get pending pledges"),
        ("Payment Management", "PUT", "/api/v1/payment-management/payment/{payment_id}", "Update payment receipt"),
        ("Payment Management", "DELETE", "/api/v1/payment-management/payment/{payment_id}", "Delete payment receipt"),
        ("Customer Ledger", "GET", "/api/v1/customer-ledger/customer/{customer_id}/statement", "Customer ledger statement"),
        ("Receipts", "GET", "/api/v1/receipts/receipt/{receipt_no}", "Get receipt details"),
        ("Daybook", "GET", "/api/v1/daybook/daily-summary", "Daily transaction summary"),
        ("Chart of Accounts", "GET", "/api/v1/coa/accounts", "Chart of accounts"),
    ]
    
    for i, (module, method, path, desc) in enumerate(key_endpoints, 1):
        method_color = {
            'GET': '🟢', 'POST': '🔵', 'PUT': '🟡', 'DELETE': '🔴'
        }.get(method, '⚪')
        
        print(f"{i:2d}. {method_color} {method:<7} {path}")
        print(f"    📖 {desc}")
        print(f"    🏷️  {module}")
        print()

if __name__ == '__main__':
    print("🔍 Scanning PawnSoft API endpoints...")
    print("Make sure the FastAPI server is running on http://localhost:8000\n")
    
    # Check if server is running
    try:
        response = requests.get(f'{BASE_URL}/docs', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️  Server responded but may have issues")
    except:
        print("❌ Server is not running. Please start the server with: python run_server.py")
        print("   Then run this script again.")
        exit(1)
    
    # Generate comprehensive API documentation
    print_comprehensive_api_list()
    print_endpoint_summary_stats()
    print_key_business_endpoints()
    
    print("\n" + "=" * 80)
    print("📚 COMPLETE API DOCUMENTATION GENERATED")
    print("=" * 80)