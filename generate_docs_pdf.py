"""
Professional PDF Documentation Generator
Creates well-formatted PDF documentation with proper layout
"""
from fpdf import FPDF
import re
import os

class DocPDF(FPDF):
    """Custom PDF class with header and footer."""
    
    def __init__(self, doc_title):
        super().__init__()
        self.doc_title = doc_title
        
    def header(self):
        if self.page_no() > 1:  # Skip header on title page
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.set_x(10)
            self.cell(95, 8, self.doc_title, align='L')
            self.cell(95, 8, f'Page {self.page_no()}', align='R')
            self.ln(12)
            self.set_x(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Prysmian - IT Department', align='C')


def sanitize(text):
    """Remove emojis and special characters."""
    if not text:
        return ""
    clean = re.sub(r'[^\x00-\x7F]+', '', str(text))
    return clean.strip()


def add_title_page(pdf, title, subtitle=""):
    """Create a professional title page."""
    pdf.add_page()
    
    # Title
    pdf.set_y(80)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(0, 82, 147)  # Blue
    pdf.multi_cell(0, 12, sanitize(title), align='C')
    
    # Subtitle
    if subtitle:
        pdf.ln(5)
        pdf.set_font('Helvetica', '', 14)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 8, sanitize(subtitle), align='C')
    
    # Company
    pdf.ln(30)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Prysmian - IT Department', align='C')
    
    # Author
    pdf.ln(50)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 'Created by Dinulescu Cosmin Ovidiu (Gemini/Claude)', align='C')


def add_section(pdf, title, content_lines):
    """Add a section with proper formatting."""
    pdf.add_page()
    
    # Section title
    pdf.set_x(10)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(0, 82, 147)
    pdf.cell(0, 12, sanitize(title))
    pdf.ln(15)
    
    # Section content
    pdf.set_text_color(0, 0, 0)
    
    for line in content_lines:
        clean = sanitize(line)
        
        if not clean:
            pdf.ln(4)
            continue
        
        pdf.set_x(10)  # Reset X position
        
        # Bullet points
        if clean.startswith('- ') or clean.startswith('* '):
            pdf.set_font('Helvetica', '', 10)
            pdf.set_x(15)
            pdf.multi_cell(180, 6, clean, align='L')
        # Sub-headers (lines ending with :)
        elif clean.endswith(':') and len(clean) < 50:
            pdf.ln(3)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_x(10)
            pdf.multi_cell(180, 7, clean, align='L')
            pdf.set_font('Helvetica', '', 10)
        # Code-like content
        elif clean.startswith('pip ') or clean.startswith('streamlit ') or ('=' in clean and not clean.startswith('-')):
            pdf.set_font('Courier', '', 9)
            pdf.set_fill_color(245, 245, 245)
            pdf.set_x(15)
            pdf.multi_cell(175, 6, clean, align='L', fill=True)
            pdf.set_font('Helvetica', '', 10)
        # Normal text
        else:
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(180, 6, clean, align='L')


def create_project_overview():
    """Generate Project Overview PDF."""
    pdf = DocPDF("Prysmian Induction Portal - Project Overview")
    pdf.set_auto_page_break(auto=True, margin=20)
    
    add_title_page(pdf, "Project Overview", "Prysmian Induction Portal")
    
    add_section(pdf, "Project Summary", [
        "A Streamlit-based employee induction/onboarding portal for Prysmian.",
        "",
        "Key Features:",
        "- Interactive step-by-step guides",
        "- Quiz system with pass/fail tracking",
        "- User progress tracking",
        "- PDF completion certificates",
        "- Admin analytics dashboard",
        "- Azure AD SSO integration ready",
    ])
    
    add_section(pdf, "Architecture", [
        "Main Entry Point:",
        "- induction.py - Application launcher",
        "",
        "Core Modules:",
        "- ui_components.py - UI rendering (sidebar, pages, guides)",
        "- data_manager.py - Data persistence and business logic",
        "- admin.py - Admin dashboard and content management",
        "- auth.py - Authentication module",
        "- sso_azure.py - Azure AD SSO integration",
        "",
        "Supporting Modules:",
        "- pdf_export.py - Analytics PDF reports",
        "- certificate.py - Completion certificate generator",
        "- search.py - Content search functionality",
        "",
        "Configuration:",
        "- content_data.json - Content database",
        "- assets/style.css - Custom styling",
    ])
    
    add_section(pdf, "Core Functions", [
        "Data Management (data_manager.py):",
        "- load_data() - Load content from JSON",
        "- save_data(data) - Persist data to JSON",
        "- get_user_id() - Get/generate user session ID",
        "- save_user_profile(name, email, dept) - Save user profile",
        "- get_user_profile() - Get current user profile",
        "",
        "Progress Tracking:",
        "- save_user_progress(category, steps) - Track completed steps",
        "- load_user_progress(category) - Load user progress",
        "- get_user_completion_status(user_id) - Detailed status",
        "",
        "Analytics:",
        "- track_page_view(category) - Track page views",
        "- track_completion(category) - Track guide completions",
        "- get_analytics_summary() - Dashboard metrics",
        "",
        "Quiz System:",
        "- get_quiz(category) - Get quiz questions",
        "- save_quiz_result(cat, score, total, passed) - Store result",
    ])
    
    add_section(pdf, "SSO Integration Points", [
        "For Azure AD SSO integration:",
        "",
        "1. User Profile:",
        "   save_user_profile(name, email, dept)",
        "   Called automatically after SSO login",
        "",
        "2. Session ID:",
        "   get_user_id() - Replace with SSO token ID",
        "",
        "3. Authentication:",
        "   require_authentication() in sso_azure.py",
        "   Forces login before app access",
    ])
    
    add_section(pdf, "Deployment", [
        "Requirements:",
        "- Python 3.9+",
        "- Streamlit 1.30+",
        "- fpdf2 (PDF generation)",
        "- msal (Azure SSO - optional)",
        "",
        "Installation:",
        "pip install streamlit fpdf2 msal",
        "",
        "Run locally:",
        "streamlit run induction.py",
    ])
    
    pdf.output("docs/PROJECT_OVERVIEW.pdf")
    print("Created: docs/PROJECT_OVERVIEW.pdf")


def create_sso_guide():
    """Generate Azure SSO Integration Guide PDF."""
    pdf = DocPDF("Azure AD SSO Integration Guide")
    pdf.set_auto_page_break(auto=True, margin=20)
    
    add_title_page(pdf, "Azure AD SSO Integration", "Step-by-Step Guide")
    
    add_section(pdf, "Prerequisites", [
        "Before starting, ensure you have:",
        "",
        "- Azure AD Tenant with admin access",
        "- Ability to create App Registrations",
        "- Python environment with pip",
        "",
        "Required package:",
        "pip install msal",
    ])
    
    add_section(pdf, "Step 1: Azure Portal Setup", [
        "1.1 Register Application:",
        "- Go to Azure Portal (portal.azure.com)",
        "- Navigate to Azure Active Directory",
        "- Select App registrations",
        "- Click New registration",
        "",
        "Configuration:",
        "- Name: Prysmian Induction Portal",
        "- Supported account types: Single tenant",
        "- Redirect URI: http://localhost:8501 (Web)",
        "",
        "1.2 Configure Authentication:",
        "- Go to Authentication tab",
        "- Add platform: Web",
        "- Add redirect URIs for production",
        "- Enable ID tokens (Implicit grant)",
        "",
        "1.3 Get Credentials:",
        "- Application (client) ID - from Overview",
        "- Directory (tenant) ID - from Overview",
        "- Client Secret - from Certificates & secrets",
    ])
    
    add_section(pdf, "Step 2: Configure Secrets", [
        "Create file: .streamlit/secrets.toml",
        "",
        "[azure]",
        "client_id = YOUR_CLIENT_ID",
        "client_secret = YOUR_CLIENT_SECRET",
        "tenant_id = YOUR_TENANT_ID",
        "redirect_uri = http://localhost:8501",
        "",
        "IMPORTANT:",
        "- Never commit secrets.toml to git",
        "- Add to .gitignore",
    ])
    
    add_section(pdf, "Step 3: Enable SSO", [
        "In induction.py, add at the beginning:",
        "",
        "from modules.sso_azure import require_authentication",
        "require_authentication()",
        "",
        "This will:",
        "- Redirect to Azure login if not authenticated",
        "- Process the OAuth callback",
        "- Auto-save user profile from SSO token",
        "- Allow app to continue once logged in",
    ])
    
    add_section(pdf, "Step 4: Update User ID", [
        "In data_manager.py, modify get_user_id():",
        "",
        "Add at the beginning of the function:",
        "sso_user = st.session_state.get('sso_user')",
        "if sso_user and sso_user.get('oid'):",
        "    return sso_user['oid']",
        "",
        "This uses Azure Object ID for consistent tracking.",
    ])
    
    add_section(pdf, "Security Notes", [
        "Production requirements:",
        "- Use HTTPS (required for OAuth)",
        "- Implement token refresh",
        "- Configure proper logout URL",
        "- Review Azure AD permissions",
    ])
    
    pdf.output("docs/AZURE_SSO_INTEGRATION.pdf")
    print("Created: docs/AZURE_SSO_INTEGRATION.pdf")


if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    create_project_overview()
    create_sso_guide()
    print("\nAll PDFs generated successfully!")
