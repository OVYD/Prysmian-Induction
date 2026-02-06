"""
PDF Export Module for Induction App
Generates PDF reports with analytics data
"""

from fpdf import FPDF
import datetime
import os
import re
from modules.data_manager import get_analytics_summary, get_analytics_data, get_all_users_progress, load_data


def sanitize_text(text):
    """Remove emojis and non-latin characters from text for PDF compatibility."""
    if not text:
        return ""
    # Remove emojis and other non-ASCII characters
    clean = re.sub(r'[^\x00-\x7F]+', '', str(text))
    return clean.strip()


class AnalyticsReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        # Logo
        logo_path = os.path.join("images", "prysmian_icon.png")
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 20)
        
        # Title
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'Induction Portal - Analytics Report', ln=True, align='C')
        
        # Date
        self.set_font('Helvetica', '', 10)
        self.cell(0, 6, f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
    
    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(28, 36, 52)  # Dark blue
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, sanitize_text(title), ln=True, fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(4)
    
    def section_header(self, text):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(0, 177, 64)  # Green
        self.cell(0, 8, sanitize_text(text), ln=True)
        self.set_text_color(0, 0, 0)
    
    def add_metric_row(self, label, value):
        self.set_font('Helvetica', '', 10)
        self.cell(80, 7, sanitize_text(label), border=0)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 7, sanitize_text(str(value)), ln=True)


def generate_analytics_pdf():
    """Generate a PDF report with analytics data."""
    pdf = AnalyticsReport()
    pdf.add_page()
    
    # Get data
    analytics = get_analytics_data()
    summary = get_analytics_summary()
    users = get_all_users_progress()
    
    # --- SECTION 1: OVERVIEW ---
    pdf.chapter_title("Overview Statistics")
    
    total_views = sum(item["views"] for item in summary)
    total_completions = sum(item["completions"] for item in summary)
    avg_rate = round(sum(item["completion_rate"] for item in summary) / len(summary), 1) if summary else 0
    
    pdf.add_metric_row("Total Page Views:", total_views)
    pdf.add_metric_row("Total Completions:", total_completions)
    pdf.add_metric_row("Average Completion Rate:", f"{avg_rate}%")
    pdf.add_metric_row("Registered Users:", len(users))
    pdf.add_metric_row("Active Guides:", len([s for s in summary if s["views"] > 0]))
    pdf.ln(8)
    
    # --- SECTION 2: GUIDE PERFORMANCE ---
    pdf.chapter_title("Guide Performance")
    
    # Table header
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(80, 8, 'Guide Name', border=1, fill=True)
    pdf.cell(30, 8, 'Views', border=1, fill=True, align='C')
    pdf.cell(35, 8, 'Completions', border=1, fill=True, align='C')
    pdf.cell(35, 8, 'Rate', border=1, fill=True, align='C', ln=True)
    
    # Table rows
    pdf.set_font('Helvetica', '', 9)
    for item in summary:
        name = sanitize_text(item["name"][:35] if len(item["name"]) > 35 else item["name"])
        pdf.cell(80, 7, name, border=1)
        pdf.cell(30, 7, str(item["views"]), border=1, align='C')
        pdf.cell(35, 7, str(item["completions"]), border=1, align='C')
        
        # Color code completion rate
        rate = item["completion_rate"]
        pdf.cell(35, 7, f"{rate}%", border=1, align='C', ln=True)
    
    pdf.ln(8)
    
    # --- SECTION 3: USER PROGRESS ---
    if users:
        pdf.add_page()
        pdf.chapter_title("User Progress Summary")
        
        completed = sum(1 for u in users if u["completion_pct"] == 100)
        in_progress = sum(1 for u in users if 0 < u["completion_pct"] < 100)
        not_started = sum(1 for u in users if u["completion_pct"] == 0)
        
        pdf.add_metric_row("Users Completed (100%):", completed)
        pdf.add_metric_row("Users In Progress:", in_progress)
        pdf.add_metric_row("Users Not Started:", not_started)
        pdf.ln(8)
        
        # User table
        pdf.section_header("Individual Progress")
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(55, 8, 'Name', border=1, fill=True)
        pdf.cell(55, 8, 'Email', border=1, fill=True)
        pdf.cell(35, 8, 'Progress', border=1, fill=True, align='C')
        pdf.cell(35, 8, 'Quizzes', border=1, fill=True, align='C', ln=True)
        
        pdf.set_font('Helvetica', '', 9)
        for user in users[:20]:  # Top 20 users
            name = sanitize_text(user["name"][:25] if len(user["name"]) > 25 else user["name"])
            email = sanitize_text(user["email"][:25] if len(user["email"]) > 25 else user["email"])
            pdf.cell(55, 7, name, border=1)
            pdf.cell(55, 7, email, border=1)
            pdf.cell(35, 7, f"{user['completion_pct']}%", border=1, align='C')
            pdf.cell(35, 7, f"{user['quizzes_passed']}/{user['total_guides']}", border=1, align='C', ln=True)
    
    # --- SECTION 4: DAILY TRENDS ---
    daily_data = analytics.get("daily_views", {})
    if daily_data:
        pdf.add_page()
        pdf.chapter_title("Last 7 Days Activity")
        
        today = datetime.datetime.now()
        for i in range(6, -1, -1):
            day = (today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            day_views = sum(daily_data.get(day, {}).values())
            day_label = datetime.datetime.strptime(day, "%Y-%m-%d").strftime("%A, %B %d")
            pdf.add_metric_row(day_label + ":", f"{day_views} views")
    
    # Generate output
    output_path = os.path.join("documents", "analytics_report.pdf")
    pdf.output(output_path)
    
    return output_path


def get_pdf_download_link():
    """Generate PDF and return file path for download."""
    try:
        path = generate_analytics_pdf()
        return path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None
