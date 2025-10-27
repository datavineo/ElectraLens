"""
Generate a sample PDF with voter data for testing the Voter Analysis Dashboard
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os
import random

# Sample data for generating random voters
first_names = [
    "Rajesh", "Priya", "Amit", "Neha", "Vikram", "Anjali", "Rohan", "Deepika",
    "Arjun", "Sneha", "Sanjay", "Pooja", "Nitin", "Kavya", "Aditya", "Shreya",
    "Manish", "Riya", "Harsh", "Divya", "Akshay", "Ananya", "Varun", "Isha",
    "Rahul", "Zara", "Karan", "Meera", "Aryan", "Nisha", "Dhruv", "Simran"
]

last_names = [
    "Kumar", "Singh", "Patel", "Sharma", "Gupta", "Verma", "Desai", "Nair",
    "Pillai", "Iyer", "Reddy", "Chopra", "Khanna", "Menon", "Rao", "Bhat",
    "Dutta", "Banerjee", "Bhattacharya", "Mukherjee", "Sen", "Ganguly", "Roy", "Chatterjee"
]

constituencies = ["North Delhi", "South Delhi", "East Delhi", "West Delhi", "Central Delhi",
                  "New Delhi", "Northeast Delhi", "Northwest Delhi"]

def generate_voter_data(count=1000):
    """Generate random voter data"""
    # Use exact column names that match database schema
    headers = ["Name", "Age", "Gender", "Constituency", "Booth No", "Address"]
    data = [headers]
    
    for i in range(count):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        age = str(random.randint(18, 80))
        gender = random.choice(["M", "F"])
        constituency = random.choice(constituencies)
        booth_no = f"{random.randint(1, 50):03d}"
        address = f"{random.randint(100, 999)} {random.choice(['Main', 'Oak', 'Elm', 'Pine', 'Maple', 'Cedar', 'Birch', 'Spruce', 'Walnut'])} St, Delhi"
        
        data.append([name, age, gender, constituency, booth_no, address])
    
    return data

def create_sample_pdf(filename="sample_voters_1000.pdf", record_count=1000):
    """Create a sample PDF with voter data - split into multiple tables for better extraction"""
    
    # Generate voter data
    voter_data = generate_voter_data(record_count)
    
    # Create PDF document
    pdf_path = os.path.join(os.path.dirname(__file__), filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=0.3*inch,
        leftMargin=0.3*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=1  # Center alignment
    )
    
    # Add title
    title = Paragraph("Voter Registration Database", title_style)
    elements.append(title)
    
    # Add metadata
    metadata = Paragraph(
        f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}<br/>"
        f"<b>Total Records:</b> {len(voter_data) - 1}",
        styles['Normal']
    )
    elements.append(metadata)
    elements.append(Spacer(1, 0.15*inch))
    
    # Split data into chunks to create multiple tables (reduces rows per page)
    chunk_size = 50  # 50 rows per table
    headers = voter_data[0]
    data_rows = voter_data[1:]
    
    for chunk_idx in range(0, len(data_rows), chunk_size):
        chunk = data_rows[chunk_idx:chunk_idx + chunk_size]
        table_data = [headers] + chunk
        
        table = Table(table_data, colWidths=[1.2*inch, 0.6*inch, 0.6*inch, 1.1*inch, 0.7*inch, 1.5*inch])
        
        # Apply table styling
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows styling
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.1*inch))
    
    # Add footer
    footer = Paragraph(
        "<i>This is a sample PDF for testing the Voter Analysis Dashboard. "
        "It contains fictional voter data for demonstration purposes.</i>",
        styles['Normal']
    )
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    return pdf_path

if __name__ == "__main__":
    print("🔄 Generating 1000 voter records across multiple tables...")
    pdf_file = create_sample_pdf(filename="sample_voters_1000.pdf", record_count=1000)
    print(f"✅ Sample PDF created successfully: {pdf_file}")
    print(f"   File size: {os.path.getsize(pdf_file) / 1024:.2f} KB")
    print(f"\n📋 PDF contains 1000 voter records split across multiple tables")
    print(f"   - 50 records per table for better extraction")
    print(f"   - Fields: Name, Age, Gender, Constituency, Booth No, Address")
    print(f"\n💡 You can now upload this PDF to the Streamlit dashboard!")
