"""
Enhanced PDF report generation with quality metrics.
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import textwrap
import os
from datetime import datetime
from typing import Dict, Any

class EnhancedReportGenerator:
    """Enhanced PDF report generator with professional formatting."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Create custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=0,  # Left alignment
            leftIndent=0,
            rightIndent=0
        )
    
    def add_title(self, title: str, subtitle: str = ""):
        """Add main title and subtitle."""
        self.story.append(Paragraph(title, self.title_style))
        if subtitle:
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=self.styles['Normal'],
                fontSize=14,
                spaceAfter=20,
                alignment=1,
                textColor=colors.grey
            )
            self.story.append(Paragraph(subtitle, subtitle_style))
        self.story.append(Spacer(1, 20))
    
    def add_quality_metrics_table(self, quality_summary: Dict[str, Any]):
        """Add quality metrics summary table."""
        self.story.append(Paragraph("Quality Assurance Summary", self.heading_style))
        
        # Prepare table data
        data = [
            ['Metric', 'Value', 'Status'],
            ['Overall Quality', 'Approved' if quality_summary['overall_approved'] else 'Issues Found', 
             '✅' if quality_summary['overall_approved'] else '⚠️'],
            ['Repositories Analyzed', str(quality_summary['repositories_analyzed']), '📊'],
            ['Files Processed', str(quality_summary['total_files_processed']), '📁'],
            ['Data Quality', 'Approved' if quality_summary['data_quality'].get('approved') else 'Issues', 
             '✅' if quality_summary['data_quality'].get('approved') else '❌'],
            ['Analysis Quality', 'Approved' if quality_summary['analysis_quality'].get('approved') else 'Issues',
             '✅' if quality_summary['analysis_quality'].get('approved') else '❌'],
            ['Final Quality', 'Approved' if quality_summary['final_quality'].get('approved') else 'Issues',
             '✅' if quality_summary['final_quality'].get('approved') else '❌']
        ]
        
        # Create table
        table = Table(data, colWidths=[2.5*inch, 2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 20))
    
    def add_section(self, title: str, content: str):
        """Add a section with title and content."""
        self.story.append(Paragraph(title, self.heading_style))
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                self.story.append(Paragraph(para.strip(), self.body_style))
        
        self.story.append(Spacer(1, 15))
    
    def add_quality_appendix(self, quality_summary: Dict[str, Any]):
        """Add detailed quality review appendix."""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Quality Review Appendix", self.title_style))
        
        # Data Quality Review
        if quality_summary['data_quality']:
            self.add_section(
                "Data Quality Review",
                quality_summary['data_quality'].get('review', 'No review available')
            )
        
        # Analysis Quality Review  
        if quality_summary['analysis_quality']:
            self.add_section(
                "Analysis Quality Review",
                quality_summary['analysis_quality'].get('review', 'No review available')
            )
        
        # Final Quality Review
        if quality_summary['final_quality']:
            self.add_section(
                "Final Quality Review",
                quality_summary['final_quality'].get('review', 'No review available')
            )
    
    def add_metadata(self, username: str):
        """Add generation metadata."""
        self.story.append(PageBreak())
        self.story.append(Paragraph("Report Metadata", self.heading_style))
        
        metadata_content = f"""
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Target: GitHub user '{username}'
System: Multi-Agent GitHub Analysis System v2.0
Quality Gates: Data Quality → Analysis Quality → Final Quality
Generated by: LostMind AI (www.LostMindAI.com)
        """
        
        self.story.append(Paragraph(metadata_content, self.body_style))
    
    def build(self):
        """Build the PDF document."""
        self.doc.build(self.story)
        return self.filename

def generate_enhanced_report(result: Dict[str, Any], output_path: str) -> str:
    """Generate enhanced PDF report with quality metrics."""
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    # Create report generator
    generator = EnhancedReportGenerator(output_path)
    
    # Add title
    generator.add_title(
        "Multi-Repository Analysis Report",
        f"Generated by Multi-Agent GitHub Analysis System v2.0"
    )
    
    # Get quality summary
    from src.workflow import get_quality_summary
    quality_summary = get_quality_summary(result)
    
    # Add quality metrics table
    generator.add_quality_metrics_table(quality_summary)
    
    # Add main report content
    generator.add_section("Executive Summary", result.get("final_report", "No report generated"))
    
    # Add quality appendix
    generator.add_quality_appendix(quality_summary)
    
    # Add metadata
    generator.add_metadata(result.get("username", "Unknown"))
    
    # Build and return path
    return generator.build()

def build_pdf(report: str, username: str, quality_summary: Dict[str, Any], outfile: str = "reports/repo_report.pdf") -> str:
    """Legacy PDF generation function for compatibility."""
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(outfile) if os.path.dirname(outfile) else ".", exist_ok=True)
    
    # Create simple PDF with reportlab canvas
    c = canvas.Canvas(outfile, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, f"GitHub Analysis Report - {username}")
    
    # Quality summary
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 100, "Quality Summary:")
    
    c.setFont("Helvetica", 12)
    quality_text = f"Overall: {'Approved' if quality_summary['overall_approved'] else 'Issues Found'}"
    c.drawString(50, height - 120, quality_text)
    
    repos_text = f"Repositories: {quality_summary['repositories_analyzed']}"
    c.drawString(50, height - 140, repos_text)
    
    files_text = f"Files: {quality_summary['total_files_processed']}"
    c.drawString(50, height - 160, files_text)
    
    # Main content
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 200, "Analysis Report:")
    
    c.setFont("Helvetica", 10)
    y = height - 230
    
    # Wrap and add report text
    for line in report.splitlines():
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50
        
        # Wrap long lines
        wrapped_lines = textwrap.wrap(line, width=100)
        if not wrapped_lines:
            wrapped_lines = [""]
            
        for wrapped_line in wrapped_lines:
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50
            c.drawString(50, y, wrapped_line)
            y -= 12
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | LostMind AI")
    
    c.save()
    return outfile