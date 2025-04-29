"""Functions for creating formatted PDF outputs of paper summaries."""

import re
from pathlib import Path

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak, Preformatted
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.colors import HexColor

def sanitize_text(text):
    """Remove problematic HTML/XML and escape special characters."""
    # Remove HTML/XML tags that might cause issues
    text = re.sub(r'<img[^>]*>', '[IMAGE]', text)
    text = re.sub(r'<[^>]*>', '', text)
    
    # Escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    # Replace problematic characters
    text = text.replace(''', "'")
    text = text.replace(''', "'")
    text = text.replace('"', '"')
    text = text.replace('"', '"')
    text = text.replace('—', '-')
    text = text.replace('–', '-')
    text = text.replace('**', '')
    
    return text

def write_summary_pdf(output_path: Path, title: str, summary: str, key_takeaways: str, engineers_corner: str):
    """Write the summary to a PDF with improved formatting and sections."""
    # Create a document with proper margins
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=1*inch,
        rightMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Get styles and create custom styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=20,
        textColor=HexColor('#2C3E50')  # Dark blue for title
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=16,
        textColor=HexColor('#2980B9')  # Blue for headings
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=12,
        textColor=HexColor('#3498DB')  # Lighter blue for subheadings
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=20,
        firstLineIndent=0,
        spaceAfter=4,
        bulletIndent=10,
        bulletFontName='Symbol'
    )
    
    # Engineer's Corner styles
    engineers_heading_style = ParagraphStyle(
        'EngineersHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=16,
        textColor=HexColor('#16A085')  # Green for Engineer's Corner
    )
    
    engineers_subheading_style = ParagraphStyle(
        'EngineersSubheading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=12,
        textColor=HexColor('#1ABC9C')  # Lighter green for subsections
    )
    
    # Key takeaways styles
    takeaways_heading_style = ParagraphStyle(
        'TakeawaysHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=16,
        textColor=HexColor('#8E44AD')  # Purple for Key Takeaways
    )
    
    takeaways_subheading_style = ParagraphStyle(
        'TakeawaysSubheading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=12,
        textColor=HexColor('#9B59B6')  # Lighter purple for subsections
    )
    
    # Build content
    story = []
    
    # Title - sanitize first
    sanitized_title = sanitize_text(title)
    story.append(Paragraph(sanitized_title + " — Engineer's Summary", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Add a brief intro paragraph
    intro = "This is an application-focused summary of research paper findings, highlighting practical insights and opportunities for engineers."
    story.append(Paragraph(intro, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Add Key Takeaways section
    story.append(Paragraph("Key Takeaways", takeaways_heading_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Process key takeaways content
    takeaways_lines = key_takeaways.split("\n")
    current_section = None
    current_text = []
    in_bullet_list = False
    bullet_items = []
    
    for line in takeaways_lines:
        line = line.strip()
        
        if not line:
            # Empty line - process current content
            if current_text:
                # Flush any bullet list first
                if in_bullet_list and bullet_items:
                    for bullet in bullet_items:
                        story.append(Paragraph("• " + bullet, bullet_style))
                    bullet_items = []
                    in_bullet_list = False
                    story.append(Spacer(1, 0.1*inch))
                
                # Then add the paragraph
                para_text = sanitize_text(" ".join(current_text))
                try:
                    story.append(Paragraph(para_text, body_style))
                    story.append(Spacer(1, 0.1*inch))
                except:
                    story.append(Preformatted(para_text, styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                current_text = []
        elif re.match(r"^#+\s+", line) or (line.startswith("Key ") and ":" in line) or line.endswith(":"):
            # This is a section heading in the key takeaways
            
            # Flush any bullet list first
            if in_bullet_list and bullet_items:
                for bullet in bullet_items:
                    story.append(Paragraph("• " + bullet, bullet_style))
                bullet_items = []
                in_bullet_list = False
                story.append(Spacer(1, 0.1*inch))
            
            # Add current content as paragraph if any
            if current_text:
                para_text = sanitize_text(" ".join(current_text))
                try:
                    story.append(Paragraph(para_text, body_style))
                except:
                    story.append(Preformatted(para_text, styles['Normal']))
                current_text = []
            
            # Extract heading text
            heading_text = re.sub(r"^#+\s+", "", line)
            if heading_text.endswith(":"):
                heading_text = heading_text[:-1]  # Remove trailing colon
            
            # Add the subheading
            story.append(Paragraph(heading_text, takeaways_subheading_style))
            current_section = heading_text
        elif line.startswith("- ") or line.startswith("* ") or line.startswith("• ") or re.match(r"^\d+\.\s+", line):
            # Process bullet point
            
            # Flush current paragraph if any
            if current_text:
                para_text = sanitize_text(" ".join(current_text))
                try:
                    story.append(Paragraph(para_text, body_style))
                except:
                    story.append(Preformatted(para_text, styles['Normal']))
                current_text = []
            
            in_bullet_list = True
            bullet_text = line
            # Remove bullet marker
            bullet_text = re.sub(r"^- ", "", bullet_text)
            bullet_text = re.sub(r"^\* ", "", bullet_text)
            bullet_text = re.sub(r"^• ", "", bullet_text)
            bullet_text = re.sub(r"^\d+\.\s+", "", bullet_text)
            
            bullet_items.append(sanitize_text(bullet_text))
        else:
            # Regular text - add to current paragraph
            if in_bullet_list and bullet_items:
                # If we're in a bullet list, assume this continues the last bullet point
                bullet_items[-1] += " " + line
            else:
                current_text.append(line)
    
    # Add any remaining content
    if in_bullet_list and bullet_items:
        for bullet in bullet_items:
            story.append(Paragraph("• " + bullet, bullet_style))
    
    if current_text:
        para_text = sanitize_text(" ".join(current_text))
        try:
            story.append(Paragraph(para_text, body_style))
        except:
            story.append(Preformatted(para_text, styles['Normal']))
    
    # Add a page break before summary
    story.append(PageBreak())
    
    # Main Summary section
    story.append(Paragraph("Research Summary", heading_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Process summary content
    sections = summary.split("\n")
    current_text = []
    in_bullet_list = False
    bullet_items = []
    
    for line in sections:
        line = line.strip()
        if not line:
            # Empty line - add current content as paragraph if any
            if current_text:
                # Flush any bullet list first
                if in_bullet_list and bullet_items:
                    for bullet in bullet_items:
                        story.append(Paragraph("• " + bullet, bullet_style))
                    bullet_items = []
                    in_bullet_list = False
                    story.append(Spacer(1, 0.1*inch))
                
                # Then add the paragraph
                para_text = sanitize_text(" ".join(current_text))
                try:
                    story.append(Paragraph(para_text, body_style))
                    story.append(Spacer(1, 0.1*inch))
                except:
                    story.append(Preformatted(para_text, styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                current_text = []
        elif line.startswith("###") or line.startswith("####"):
            # Flush any bullet list first
            if in_bullet_list and bullet_items:
                for bullet in bullet_items:
                    story.append(Paragraph("• " + bullet, bullet_style))
                bullet_items = []
                in_bullet_list = False
                story.append(Spacer(1, 0.1*inch))
                
            # Add current content as paragraph if any
            if current_text:
                para_text = sanitize_text(" ".join(current_text))
                try:
                    story.append(Paragraph(para_text, body_style))
                except:
                    story.append(Preformatted(para_text, styles['Normal']))
                current_text = []
            
            # Add subheading
            heading_text = sanitize_text(line.replace("###", "").replace("####", "").strip())
            story.append(Paragraph(heading_text, subheading_style))
        elif line.startswith("##") or line.startswith("**") and line.endswith("**") or line.endswith(":"):
            # Flush any bullet list first
            if in_bullet_list and bullet_items:
                for bullet in bullet_items:
                    story.append(Paragraph("• " + bullet, bullet_style))
                bullet_items = []
                in_bullet_list = False
                story.append(Spacer(1, 0.1*inch))
                
            # Add current content as paragraph if any
            if current_text:
                para_text = sanitize_text(" ".join(current_text))
                try:
                    story.append(Paragraph(para_text, body_style))
                except:
                    story.append(Preformatted(para_text, styles['Normal']))
                current_text = []
            
            # Add heading
            heading_text = sanitize_text(line.replace("##", "").replace("**", "").strip())
            if heading_text.endswith(":"):
                heading_text = heading_text[:-1]  # Remove trailing colon
            story.append(Paragraph(heading_text, heading_style))
        elif line.startswith("- ") or line.startswith("* ") or line.startswith("• ") or re.match(r"^\d+\.\s+", line):
            # Flush current paragraph if any
            if current_text:
                para_text = sanitize_text(" ".join(current_text))
                try:
                    story.append(Paragraph(para_text, body_style))
                except:
                    story.append(Preformatted(para_text, styles['Normal']))
                current_text = []
            
            # Process bullet point
            in_bullet_list = True
            bullet_text = line
            # Remove bullet marker
            bullet_text = re.sub(r"^- ", "", bullet_text)
            bullet_text = re.sub(r"^\* ", "", bullet_text)
            bullet_text = re.sub(r"^• ", "", bullet_text)
            bullet_text = re.sub(r"^\d+\.\s+", "", bullet_text)
            
            # Handle bold formatting
            if "**" in bullet_text:
                bullet_text = bullet_text.replace("**", "<b>", 1)
                bullet_text = bullet_text.replace("**", "</b>", 1)
            
            bullet_items.append(sanitize_text(bullet_text))
        elif line.startswith("\t") or line.startswith("    "):
            # This is a continuation of a bullet point
            if in_bullet_list and bullet_items:
                # Append to the last bullet point
                bullet_items[-1] += " " + line.strip()
            else:
                # Or treat as regular text
                current_text.append(line)
        else:
            # Regular text - add to current paragraph
            current_text.append(line)
    
    # Add any remaining content
    if in_bullet_list and bullet_items:
        for bullet in bullet_items:
            story.append(Paragraph("• " + bullet, bullet_style))
        story.append(Spacer(1, 0.1*inch))
    
    if current_text:
        para_text = sanitize_text(" ".join(current_text))
        try:
            story.append(Paragraph(para_text, body_style))
        except:
            story.append(Preformatted(para_text, styles['Normal']))
    
    # Add a page break before Engineer's Corner
    story.append(PageBreak())
    
    # Engineer's Corner section
    story.append(Paragraph("Engineer's Corner", engineers_heading_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Process Engineer's Corner content in a similar manner to Key Takeaways
    # ...similar processing code for engineers_corner...
    engineers_lines = engineers_corner.split("\n")
    current_section = None
    current_text = []
    in_bullet_list = False
    bullet_items = []
    
    for line in engineers_lines:
        line = line.strip()
        
        if not line:
            # Empty line - process current content
            if current_text:
                # Flush any bullet list first
                if in_bullet_list and bullet_items:
                    for bullet in bullet_items:
                        story.append(Paragraph("• " + bullet, bullet_style))
                    bullet_items = []
                    in_bullet_list = False
                    story.append(Spacer(1, 0.1*inch))
                
                # Then add the paragraph
                para_text = sanitize_text(" ".join(current_text))
                try:
                    story.append(Paragraph(para_text, body_style))
                    story.append(Spacer(1, 0.1*inch))
                except:
                    story.append(Preformatted(para_text, styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                current_text = []
        elif re.match(r"^#+\s+", line) or (line.startswith("Practical") and ":" in line) or line.endswith(":"):
            # This is a section heading in the Engineer's Corner
            
            # Flush any bullet list first
            if in_bullet_list and bullet_items:
                for bullet in bullet_items:
                    story.append(Paragraph("• " + bullet, bullet_style))
                bullet_items = []
                in_bullet_list = False
                story.append(Spacer(1, 0.1*inch))
            
            # Add current content as paragraph if any
            if current_text:
                para_text = sanitize_text(" ".join(current_text))
                try:
                    story.append(Paragraph(para_text, body_style))
                except:
                    story.append(Preformatted(para_text, styles['Normal']))
                current_text = []
            
            # Extract heading text
            heading_text = re.sub(r"^#+\s+", "", line)
            if heading_text.endswith(":"):
                heading_text = heading_text[:-1]  # Remove trailing colon
            
            # Add the subheading
            story.append(Paragraph(heading_text, engineers_subheading_style))
            current_section = heading_text
        elif line.startswith("- ") or line.startswith("* ") or line.startswith("• ") or re.match(r"^\d+\.\s+", line):
            # Process bullet point
            
            # Flush current paragraph if any
            if current_text:
                para_text = sanitize_text(" ".join(current_text))
                try:
                    story.append(Paragraph(para_text, body_style))
                except:
                    story.append(Preformatted(para_text, styles['Normal']))
                current_text = []
            
            in_bullet_list = True
            bullet_text = line
            # Remove bullet marker
            bullet_text = re.sub(r"^- ", "", bullet_text)
            bullet_text = re.sub(r"^\* ", "", bullet_text)
            bullet_text = re.sub(r"^• ", "", bullet_text)
            bullet_text = re.sub(r"^\d+\.\s+", "", bullet_text)
            
            bullet_items.append(sanitize_text(bullet_text))
        else:
            # Regular text - add to current paragraph
            if in_bullet_list and bullet_items:
                # If we're in a bullet list, assume this continues the last bullet point
                bullet_items[-1] += " " + line
            else:
                current_text.append(line)
    
    # Add any remaining content
    if in_bullet_list and bullet_items:
        for bullet in bullet_items:
            story.append(Paragraph("• " + bullet, bullet_style))
    
    if current_text:
        para_text = sanitize_text(" ".join(current_text))
        try:
            story.append(Paragraph(para_text, body_style))
        except:
            story.append(Preformatted(para_text, styles['Normal']))
    
    # Build the PDF
    doc.build(story)