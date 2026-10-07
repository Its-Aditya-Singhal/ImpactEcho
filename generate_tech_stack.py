#!/usr/bin/env python3
"""
Generate ImpactEcho Tech Stack PDF
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def create_tech_stack_pdf():
    """Generate comprehensive tech stack PDF"""
    
    filename = "ImpactEcho_Tech_Stack.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#8b5cf6'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#94a3b8'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#ff006e'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#8b5cf6'),
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1a0b2e'),
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Header
    elements.append(Paragraph("ImpactEcho", title_style))
    elements.append(Paragraph("Complete Technology Stack Documentation", subtitle_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Project Overview
    elements.append(Paragraph("📋 Project Overview", heading_style))
    overview_text = """
    ImpactEcho is a blockchain-powered donation platform that ensures transparency and accountability 
    in charitable giving. The platform features MetaMask integration for secure transactions, 
    AI-powered bill verification for NGOs, an intelligent chatbot for donor engagement, and comprehensive 
    admin controls for platform management.
    """
    elements.append(Paragraph(overview_text, body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Tech Stack Categories
    tech_stack = [
        {
            "category": "🎨 Frontend Technologies",
            "icon": "🎨",
            "items": [
                ("HTML5", "Markup language for structuring web content", "Core"),
                ("CSS3", "Styling with custom properties, gradients, animations", "Core"),
                ("JavaScript (ES6+)", "Client-side logic and interactivity", "Core"),
                ("Responsive Design", "Mobile-first approach with media queries", "Core"),
            ]
        },
        {
            "category": "🎭 Frontend Frameworks & Libraries",
            "icon": "🎭",
            "items": [
                ("jsPDF", "Client-side PDF generation for receipts", "v2.5.1"),
                ("Ethers.js", "Ethereum blockchain interaction library", "v5.7.2"),
                ("Google Fonts (Inter)", "Typography enhancement", "Web Fonts"),
            ]
        },
        {
            "category": "🔧 Backend Technologies",
            "icon": "🔧",
            "items": [
                ("Python", "Server-side programming language", "v3.x"),
                ("Flask", "Lightweight WSGI web application framework", "Latest"),
                ("Flask Session", "Session management for user authentication", "Built-in"),
                ("Werkzeug", "WSGI utility library (Flask dependency)", "Latest"),
            ]
        },
        {
            "category": "💾 Data Storage & Management",
            "icon": "💾",
            "items": [
                ("JSON Files", "Primary data storage (causes.json, users.json, etc.)", "Native"),
                ("LocalStorage", "Client-side data persistence for user sessions", "Browser API"),
                ("File System", "Document and image uploads storage", "OS Native"),
            ]
        },
        {
            "category": "⛓️ Blockchain Technologies",
            "icon": "⛓️",
            "items": [
                ("Solidity", "Smart contract programming language", "v0.8.x"),
                ("Foundry", "Ethereum development framework", "Latest"),
                ("Anvil", "Local Ethereum node for testing", "Foundry"),
                ("Forge", "Solidity testing framework", "Foundry"),
                ("MetaMask", "Web3 wallet integration", "Browser Extension"),
                ("Sepolia Testnet", "Ethereum test network", "Public"),
                ("Chainlink Price Feeds", "Real-time ETH/USD conversion", "Aggregator"),
            ]
        },
        {
            "category": "🤖 Artificial Intelligence & Machine Learning",
            "icon": "🤖",
            "items": [
                ("Pytesseract", "OCR engine for bill text extraction", "Latest"),
                ("Tesseract OCR", "Google's OCR engine", "Latest"),
                ("Pillow (PIL)", "Image processing library", "Latest"),
                ("Custom NLP", "Rule-based natural language processing for chatbot", "Custom"),
                ("Pattern Recognition", "Regex-based amount extraction from bills", "Python re"),
                ("Risk Assessment", "8-point scoring system for bill verification", "Custom Algorithm"),
            ]
        },
        {
            "category": "📄 Document Generation",
            "icon": "📄",
            "items": [
                ("ReportLab", "Python PDF generation library", "Latest"),
                ("jsPDF", "JavaScript PDF generation", "v2.5.1"),
                ("PDF Templates", "Custom contract and receipt templates", "Custom"),
            ]
        },
        {
            "category": "🔐 Security & Authentication",
            "icon": "🔐",
            "items": [
                ("Flask Sessions", "Secure server-side session management", "Built-in"),
                ("MetaMask Signature", "Cryptographic wallet authentication", "Web3"),
                ("Password Protection", "Admin and NGO login security", "Custom"),
                ("File Upload Validation", "Whitelist-based file type checking", "Custom"),
                ("CORS Handling", "Cross-origin resource sharing", "Flask-CORS"),
            ]
        },
        {
            "category": "🎨 UI/UX Design Libraries",
            "icon": "🎨",
            "items": [
                ("CSS Variables", "Dynamic theming with custom properties", "Native CSS"),
                ("CSS Animations", "Keyframe animations and transitions", "Native CSS"),
                ("CSS Gradients", "Linear and radial gradients for styling", "Native CSS"),
                ("Glassmorphism", "Modern frosted glass effect design", "Custom CSS"),
                ("Flexbox", "Flexible box layout system", "Native CSS"),
                ("CSS Grid", "Two-dimensional grid layout", "Native CSS"),
            ]
        },
        {
            "category": "📊 Data Visualization & Display",
            "icon": "📊",
            "items": [
                ("Custom Progress Bars", "Donation goal tracking visualization", "Custom CSS/JS"),
                ("Real-time Stats", "Live donation statistics updates", "JavaScript"),
                ("Badge System", "Donor ranking with 5 levels", "Custom"),
                ("Dynamic Tables", "Admin panel data display", "HTML/JS"),
            ]
        },
        {
            "category": "🔄 APIs & Endpoints",
            "icon": "🔄",
            "items": [
                ("RESTful API", "Flask-based REST endpoints", "Custom"),
                ("JSON API", "Data exchange format", "Native"),
                ("File Upload API", "Multipart form data handling", "Flask"),
                ("Webhook Support", "Event-driven notifications", "Custom"),
            ]
        },
        {
            "category": "🧪 Testing & Development",
            "icon": "🧪",
            "items": [
                ("Foundry Test Suite", "Solidity smart contract testing", "Forge"),
                ("Python Debug Mode", "Flask development server debugging", "Flask"),
                ("Console Logging", "JavaScript debugging and monitoring", "Browser DevTools"),
                ("Local Blockchain", "Anvil for local testing", "Foundry"),
            ]
        },
        {
            "category": "📦 Package Managers & Build Tools",
            "icon": "📦",
            "items": [
                ("pip", "Python package installer", "Latest"),
                ("npm/npx", "Node package manager (for blockchain tools)", "Latest"),
                ("Foundry Toolkit", "Smart contract development tools", "Latest"),
            ]
        },
        {
            "category": "🌐 Web Technologies & Standards",
            "icon": "🌐",
            "items": [
                ("HTTP/HTTPS", "Web communication protocols", "Standard"),
                ("WebSocket", "Real-time bidirectional communication", "Browser API"),
                ("AJAX", "Asynchronous data fetching", "XMLHttpRequest/Fetch"),
                ("JSON", "Data interchange format", "Standard"),
                ("REST Architecture", "API design pattern", "Standard"),
            ]
        },
        {
            "category": "🖼️ Media & Assets",
            "icon": "🖼️",
            "items": [
                ("PNG/JPG/WebP", "Image formats", "Standard"),
                ("PDF", "Document format", "Standard"),
                ("SVG", "Scalable vector graphics", "Web Standard"),
                ("Base64 Encoding", "Image data encoding", "Standard"),
            ]
        },
        {
            "category": "🔧 Development Tools",
            "icon": "🔧",
            "items": [
                ("Git", "Version control system", "Latest"),
                ("GitHub", "Code hosting platform", "Cloud"),
                ("VS Code / Cursor", "Code editor", "IDE"),
                ("Terminal/Shell", "Command-line interface", "Bash/Zsh"),
                ("Python Virtual Environment", "Isolated Python environment", "venv"),
            ]
        },
        {
            "category": "🚀 Deployment & Hosting",
            "icon": "🚀",
            "items": [
                ("Flask Development Server", "Local development server", "Flask"),
                ("WSGI", "Python web server gateway interface", "Standard"),
                ("Network Hosting", "Local network accessibility (0.0.0.0)", "Custom"),
                ("Port 8000", "Application server port", "Custom"),
            ]
        },
        {
            "category": "📱 Browser Technologies",
            "icon": "📱",
            "items": [
                ("LocalStorage API", "Client-side data storage", "Web API"),
                ("SessionStorage API", "Session-scoped storage", "Web API"),
                ("Fetch API", "Modern AJAX replacement", "Web API"),
                ("DOM Manipulation", "Dynamic HTML updates", "JavaScript"),
                ("Event Listeners", "User interaction handling", "JavaScript"),
            ]
        },
        {
            "category": "🎯 Smart Contract Architecture",
            "icon": "🎯",
            "items": [
                ("FundMe.sol", "Main donation contract", "Custom Solidity"),
                ("PriceConverter.sol", "ETH to USD conversion library", "Custom Solidity"),
                ("AggregatorV3Interface", "Chainlink price feed interface", "Chainlink"),
                ("Modifiers", "Access control and validation", "Solidity"),
                ("Events", "Blockchain event logging", "Solidity"),
            ]
        },
        {
            "category": "💼 Business Logic Components",
            "icon": "💼",
            "items": [
                ("User Management", "Donor account handling", "Python/Flask"),
                ("NGO Registration System", "Organization onboarding", "Python/Flask"),
                ("Cause Management", "Donation campaign creation", "Python/Flask"),
                ("Transaction Logging", "Donation history tracking", "Python/Flask"),
                ("Admin Panel", "Platform administration", "Python/Flask/JavaScript"),
                ("Contract Generation", "Legal document creation", "Python/ReportLab"),
                ("AI Verification", "Bill authenticity checking", "Python/ML"),
                ("Notification System", "User and admin alerts", "Python/JavaScript"),
            ]
        },
        {
            "category": "🎨 Design System",
            "icon": "🎨",
            "items": [
                ("Color Scheme", "Purple (#8b5cf6) & Pink (#ff006e) gradient theme", "Custom"),
                ("Typography", "Inter font family", "Google Fonts"),
                ("Spacing System", "Consistent padding and margins", "Custom"),
                ("Border Radius", "Rounded corners (8px, 12px, 16px)", "Custom"),
                ("Shadow System", "Layered elevation effects", "Custom CSS"),
                ("Animation Timing", "Smooth transitions (0.3s ease)", "Custom"),
            ]
        },
    ]
    
    # Add each category
    for category_data in tech_stack:
        elements.append(Paragraph(category_data["category"], heading_style))
        
        # Create table data
        table_data = [["Technology", "Description", "Version/Type"]]
        
        for item in category_data["items"]:
            tech, desc, version = item
            table_data.append([tech, desc, version])
        
        # Create table
        table = Table(table_data, colWidths=[2*inch, 3.5*inch, 1.2*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1a0b2e')),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Add new page for additional info
    elements.append(PageBreak())
    
    # Key Features
    elements.append(Paragraph("🌟 Key Technical Features", heading_style))
    
    features = [
        ("MetaMask Integration", "Secure Web3 wallet authentication and blockchain transactions"),
        ("AI Bill Verification", "8-point scoring system with OCR for document authenticity"),
        ("Smart Chatbot", "Context-aware AI assistant with natural language understanding"),
        ("Real-time Updates", "Live dashboard statistics and donation tracking"),
        ("Blockchain Transparency", "On-chain verification of all donations"),
        ("PDF Generation", "Professional receipts and legal contracts"),
        ("Multi-user System", "Admin, NGO, and Donor portals with role-based access"),
        ("Responsive Design", "Mobile-first approach with cross-device compatibility"),
        ("Progress Tracking", "Visual donation goals with real-time updates"),
        ("Badge System", "5-tier donor ranking system"),
        ("Transaction History", "Complete audit trail with downloadable receipts"),
        ("Contract Management", "Automated legal document generation and signing"),
    ]
    
    for feature, description in features:
        elements.append(Paragraph(f"<b>{feature}:</b> {description}", body_style))
        elements.append(Spacer(1, 0.08*inch))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # File Structure
    elements.append(Paragraph("📁 Project File Structure", heading_style))
    
    file_structure = """
    <b>Backend Files:</b><br/>
    • app.py - Main Flask application (1700+ lines)<br/>
    • Various JSON data files (users.json, causes.json, etc.)<br/>
    <br/>
    <b>Frontend Files:</b><br/>
    • templates/ - HTML templates (dash.html, admin.html, etc.)<br/>
    • static/ - CSS and JavaScript files<br/>
    • static/script.js - Main dashboard logic<br/>
    • static/chatbot.js - AI chatbot implementation<br/>
    • static/style.css, style2.css, chatbot.css - Styling<br/>
    <br/>
    <b>Blockchain Files:</b><br/>
    • foundry/ - Smart contract development<br/>
    • foundry/src/FundMe.sol - Main donation contract<br/>
    • foundry/src/PriceConverter.sol - Price conversion library<br/>
    • foundry/test/ - Contract test suite<br/>
    • static/blockchain.js - Web3 integration<br/>
    <br/>
    <b>Data Storage:</b><br/>
    • causes.json - Active donation campaigns<br/>
    • users.json - Registered users<br/>
    • ngo_registrations.json - NGO applications<br/>
    • verification_requests.json - AI verification queue<br/>
    • uploads/ - User-uploaded files<br/>
    """
    
    elements.append(Paragraph(file_structure, body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Statistics
    elements.append(Paragraph("📊 Project Statistics", heading_style))
    
    stats_data = [
        ["Metric", "Count"],
        ["Total Lines of Code", "5000+"],
        ["Python Files", "1 (main app.py)"],
        ["JavaScript Files", "3 (script.js, chatbot.js, blockchain.js)"],
        ["HTML Templates", "7"],
        ["CSS Files", "3"],
        ["Solidity Contracts", "3"],
        ["JSON Data Files", "10+"],
        ["API Endpoints", "40+"],
        ["Features", "30+"],
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff006e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fff7f0'), colors.white]),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", footer_style))
    elements.append(Paragraph("ImpactEcho - Amplifying Generosity Worldwide", footer_style))
    elements.append(Paragraph("© 2024 ImpactEcho. All rights reserved.", footer_style))
    elements.append(Paragraph("Generated with ❤️ using Python & ReportLab", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    return filename

if __name__ == "__main__":
    print("🚀 Generating ImpactEcho Tech Stack PDF...")
    filename = create_tech_stack_pdf()
    print(f"✅ PDF generated successfully: {filename}")
    print(f"📍 Location: {os.path.abspath(filename)}")

