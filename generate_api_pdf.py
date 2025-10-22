#!/usr/bin/env python3
"""
PawnSoft API Documentation PDF Generator
Converts the complete API endpoints list to a professional PDF document
"""
import requests
import json
from datetime import datetime
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os

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

def create_pdf_styles():
    """Create custom PDF styles"""
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=HexColor('#2E3B4E')
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=HexColor('#1E88E5'),
        backColor=HexColor('#F5F5F5'),
        borderWidth=1,
        borderColor=HexColor('#E0E0E0'),
        leftIndent=10,
        rightIndent=10,
        topPadding=8,
        bottomPadding=8
    )
    
    # Subheading style
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=15,
        textColor=HexColor('#424242')
    )
    
    # Normal text style
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leftIndent=20
    )
    
    # Code style
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Courier',
        textColor=HexColor('#D32F2F'),
        backColor=HexColor('#FAFAFA'),
        leftIndent=25,
        rightIndent=10,
        topPadding=3,
        bottomPadding=3
    )
    
    return {
        'title': title_style,
        'heading': heading_style,
        'subheading': subheading_style,
        'normal': normal_style,
        'code': code_style
    }

def get_method_color(method):
    """Get color for HTTP method"""
    colors_map = {
        'GET': HexColor('#4CAF50'),      # Green
        'POST': HexColor('#2196F3'),     # Blue  
        'PUT': HexColor('#FF9800'),      # Orange
        'DELETE': HexColor('#F44336'),   # Red
        'PATCH': HexColor('#9C27B0')     # Purple
    }
    return colors_map.get(method, HexColor('#757575'))

def create_api_pdf():
    """Create a comprehensive PDF documentation of all API endpoints"""
    
    print("🔍 Fetching API endpoints...")
    openapi_data = get_api_endpoints()
    if not openapi_data:
        print("❌ Could not retrieve API endpoints. Make sure the server is running.")
        return None
    
    endpoints_by_tag = format_endpoints_by_module(openapi_data)
    if not endpoints_by_tag:
        print("❌ No endpoints found")
        return None
    
    # Create PDF file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"PawnSoft_API_Documentation_{timestamp}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4, 
                          rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = create_pdf_styles()
    story = []
    
    # Title page
    story.append(Paragraph("PawnSoft API Documentation", styles['title']))
    story.append(Spacer(1, 12))
    
    # Summary statistics
    total_endpoints = sum(len(endpoints) for endpoints in endpoints_by_tag.values())
    method_counts = {'GET': 0, 'POST': 0, 'PUT': 0, 'DELETE': 0, 'PATCH': 0}
    
    for tag, endpoints in endpoints_by_tag.items():
        for endpoint in endpoints:
            method = endpoint['method']
            if method in method_counts:
                method_counts[method] += 1
    
    # Summary table
    summary_data = [
        ['Statistic', 'Count'],
        ['Total Endpoints', str(total_endpoints)],
        ['Total Modules', str(len(endpoints_by_tag))],
        ['GET Endpoints', str(method_counts['GET'])],
        ['POST Endpoints', str(method_counts['POST'])],
        ['PUT Endpoints', str(method_counts['PUT'])],
        ['DELETE Endpoints', str(method_counts['DELETE'])],
        ['Generation Date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1E88E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8F9FA')),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#E0E0E0'))
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # API Access Information
    story.append(Paragraph("API Access Information", styles['subheading']))
    access_info = [
        f"<b>Base URL:</b> {BASE_URL}",
        f"<b>Swagger UI:</b> {BASE_URL}/docs",
        f"<b>ReDoc:</b> {BASE_URL}/redoc",
        f"<b>OpenAPI JSON:</b> {BASE_URL}/openapi.json"
    ]
    
    for info in access_info:
        story.append(Paragraph(info, styles['normal']))
    
    story.append(PageBreak())
    
    # Module order for better organization
    module_order = [
        'Pledge Payments', 'Payment Management', 'Customer Ledger Reports', 
        'Payment Receipts', 'Chart of Accounts', 'Daybook', 'Untagged'
    ]
    
    # Process each module
    for module in module_order:
        if module in endpoints_by_tag:
            endpoints = endpoints_by_tag[module]
            
            # Module title
            story.append(Paragraph(f"{module} ({len(endpoints)} endpoints)", styles['heading']))
            
            # Create endpoints table for this module
            table_data = [['#', 'Method', 'Endpoint', 'Description']]
            
            for i, endpoint in enumerate(endpoints, 1):
                method = endpoint['method']
                path = endpoint['path']
                summary = endpoint['summary']
                
                # Truncate long paths and summaries for table
                if len(path) > 45:
                    path = path[:42] + "..."
                if len(summary) > 50:
                    summary = summary[:47] + "..."
                
                table_data.append([
                    str(i),
                    method,
                    path,
                    summary
                ])
            
            # Create table
            col_widths = [0.5*inch, 1*inch, 2.5*inch, 2.5*inch]
            endpoints_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Style the table
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E3B4E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#FAFAFA')),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#E0E0E0')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]
            
            # Add method-specific colors
            for i, endpoint in enumerate(endpoints, 1):
                method = endpoint['method']
                method_color = get_method_color(method)
                table_style.append(('TEXTCOLOR', (1, i), (1, i), method_color))
                table_style.append(('FONTNAME', (1, i), (1, i), 'Helvetica-Bold'))
            
            endpoints_table.setStyle(TableStyle(table_style))
            story.append(endpoints_table)
            story.append(Spacer(1, 15))
            
            # Add detailed endpoint information for key modules
            if module in ['Pledge Payments', 'Payment Management', 'Customer Ledger Reports']:
                story.append(Paragraph("Detailed Endpoint Information:", styles['subheading']))
                
                for endpoint in endpoints[:5]:  # Show first 5 endpoints in detail
                    method = endpoint['method']
                    path = endpoint['path']
                    summary = endpoint['summary']
                    
                    # Endpoint details
                    method_color_hex = get_method_color(method).hexval()
                    endpoint_title = f'<font color="{method_color_hex}"><b>{method}</b></font> {path}'
                    story.append(Paragraph(endpoint_title, styles['code']))
                    story.append(Paragraph(f"<b>Description:</b> {summary}", styles['normal']))
                    
                    # Parameters
                    params = endpoint.get('parameters', [])
                    if params:
                        path_params = [p for p in params if p.get('in') == 'path']
                        query_params = [p for p in params if p.get('in') == 'query']
                        
                        if path_params:
                            path_param_names = [p.get('name', 'N/A') for p in path_params]
                            story.append(Paragraph(f"<b>Path Parameters:</b> {', '.join(path_param_names)}", styles['normal']))
                        
                        if query_params:
                            query_param_names = [p.get('name', 'N/A') for p in query_params]
                            story.append(Paragraph(f"<b>Query Parameters:</b> {', '.join(query_param_names)}", styles['normal']))
                    
                    if endpoint.get('request_body'):
                        story.append(Paragraph("<b>Request Body:</b> Required", styles['normal']))
                    
                    story.append(Spacer(1, 8))
            
            story.append(PageBreak())
    
    # Key Business Endpoints section
    story.append(Paragraph("Key Business Endpoints", styles['heading']))
    
    key_endpoints = [
        ("Authentication", "POST", "/token", "Login for access token"),
        ("Customers", "GET", "/customers", "List all customers"),  
        ("Pledges", "POST", "/pledges", "Create new pledge"),
        ("Multiple Payments", "POST", "/api/v1/pledge-payments/customers/{id}/multiple-payment", "Multiple pledge payment"),
        ("Pending Pledges", "GET", "/api/v1/pledge-payments/customers/{id}/pending", "Get pending pledges"),
        ("Update Payment", "PUT", "/api/v1/payment-management/payment/{id}", "Update payment receipt"),
        ("Delete Payment", "DELETE", "/api/v1/payment-management/payment/{id}", "Delete payment receipt"),
        ("Customer Ledger", "GET", "/api/v1/customer-ledger/customer/{id}/statement", "Customer ledger statement"),
        ("Receipt Details", "GET", "/api/v1/receipts/receipt/{receipt_no}", "Get receipt details"),
        ("Daily Summary", "GET", "/api/v1/daybook/daily-summary", "Daily transaction summary"),
    ]
    
    key_table_data = [['Module', 'Method', 'Endpoint', 'Description']]
    for module, method, path, desc in key_endpoints:
        if len(path) > 40:
            path = path[:37] + "..."
        if len(desc) > 35:
            desc = desc[:32] + "..."
        key_table_data.append([module, method, path, desc])
    
    key_table = Table(key_table_data, colWidths=[1.2*inch, 0.8*inch, 2.2*inch, 2.3*inch], repeatRows=1)
    key_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1E88E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8F9FA')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#E0E0E0')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    
    # Color code methods in key endpoints
    for i, (_, method, _, _) in enumerate(key_endpoints, 1):
        method_color = get_method_color(method)
        key_table.setStyle(TableStyle([
            ('TEXTCOLOR', (1, i), (1, i), method_color),
            ('FONTNAME', (1, i), (1, i), 'Helvetica-Bold')
        ]))
    
    story.append(key_table)
    
    # Build PDF
    print(f"📄 Generating PDF: {pdf_filename}")
    doc.build(story)
    
    return pdf_filename

if __name__ == '__main__':
    print("🚀 PawnSoft API Documentation PDF Generator")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f'{BASE_URL}/docs', timeout=5)
        if response.status_code != 200:
            print("⚠️  Server responded but may have issues")
    except:
        print("❌ Server is not running. Please start the server with: python run_server.py")
        print("   Then run this script again.")
        exit(1)
    
    # Check if reportlab is installed
    try:
        import reportlab
        print("✅ ReportLab library found")
    except ImportError:
        print("❌ ReportLab library not found. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab"])
        print("✅ ReportLab installed successfully")
    
    # Generate PDF
    pdf_file = create_api_pdf()
    
    if pdf_file:
        print(f"\n🎉 SUCCESS! PDF generated: {pdf_file}")
        print(f"📄 File size: {os.path.getsize(pdf_file) / 1024:.1f} KB")
        print(f"📁 Location: {os.path.abspath(pdf_file)}")
        
        # Try to open the PDF
        import platform
        if platform.system() == 'Windows':
            os.startfile(pdf_file)
            print("🖥️  PDF opened in default viewer")
    else:
        print("❌ Failed to generate PDF")
    
    print("\n" + "=" * 60)
    print("📚 PAWNSOFT API DOCUMENTATION PDF COMPLETE")