"""
Convert Markdown documentation to PDF
"""
from fpdf import FPDF
import re
import os

def sanitize(text):
    """Remove emojis and limit line width."""
    if not text:
        return ""
    clean = re.sub(r'[^\x00-\x7F]+', '', str(text))
    return clean.strip()

def create_doc_pdf(title, sections, output_path):
    """Create a professional documentation PDF."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title page
    pdf.set_font('Helvetica', 'B', 24)
    pdf.ln(40)
    pdf.multi_cell(190, 12, sanitize(title), align='C')
    pdf.ln(20)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(190, 10, 'Prysmian - IT Department', align='C')
    pdf.ln(60)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(190, 8, 'Created by Dinulescu Cosmin Ovidiu (Gemini/Claude)', align='C')
    
    for section_title, content in sections:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 16)
        pdf.multi_cell(190, 10, sanitize(section_title))
        pdf.ln(5)
        
        pdf.set_font('Helvetica', '', 10)
        for line in content:
            clean_line = sanitize(line)
            if not clean_line:
                pdf.ln(3)
                continue
            # Break into chunks of max 80 chars
            while len(clean_line) > 80:
                pdf.multi_cell(190, 5, clean_line[:80])
                clean_line = clean_line[80:]
            if clean_line:
                pdf.multi_cell(190, 5, clean_line)
    
    pdf.output(output_path)
    print(f"Created: {output_path}")

# ========== PROJECT OVERVIEW ==========
project_sections = [
    ("Project Summary", [
        "A Streamlit-based employee induction/onboarding portal for Prysmian Group.",
        "Features interactive guides, quizzes, progress tracking, and completion certificates.",
        "",
        "Technology Stack:",
        "- Python 3.9+",
        "- Streamlit 1.30+",
        "- fpdf2 (PDF generation)",
        "- msal (Azure SSO)",
    ]),
    ("Architecture", [
        "induction.py - Main entry point",
        "",
        "modules/ui_components.py - UI rendering (sidebar, pages, guides)",
        "modules/data_manager.py - Data persistence & business logic",
        "modules/admin.py - Admin dashboard",
        "modules/auth.py - Authentication",
        "modules/sso_azure.py - Azure AD SSO integration",
        "modules/pdf_export.py - PDF report generation",
        "modules/certificate.py - Certificate generation",
        "modules/search.py - Search functionality",
        "",
        "assets/style.css - Custom CSS styling",
        "content_data.json - Content database",
    ]),
    ("Core Functions - data_manager.py", [
        "load_data() - Load content from JSON",
        "save_data(data) - Persist data to JSON",
        "get_user_id() - Get/generate user session ID",
        "save_user_profile(name, email, dept) - SSO Integration Point",
        "get_user_profile() - Get current user profile",
        "save_user_progress(cat, steps) - Track completed steps",
        "load_user_progress(cat) - Load user progress",
        "track_page_view(cat) - Analytics: page views",
        "track_completion(cat) - Analytics: completions",
        "get_analytics_summary() - Dashboard metrics",
        "get_quiz(cat) - Get quiz questions",
        "save_quiz_result(cat, score, total, passed) - Store quiz result",
        "get_all_users_progress() - Admin: all users data",
        "get_user_completion_status(user_id) - Detailed user progress",
    ]),
    ("Authentication Functions - auth.py", [
        "hash_password(pw) - SHA-256 password hash",
        "verify_password(hash, pw) - Verify password",
        "login_sidebar() - Admin login UI",
    ]),
    ("PDF Functions", [
        "pdf_export.py:",
        "- generate_analytics_pdf() - Create analytics PDF report",
        "- get_pdf_download_link() - Generate & return PDF path",
        "",
        "certificate.py:",
        "- generate_certificate(name, email) - Create PDF certificate",
        "- can_get_certificate() - Check eligibility",
    ]),
    ("SSO Functions - sso_azure.py", [
        "require_authentication() - Force login if not authenticated",
        "get_current_user() - Get authenticated user info",
        "is_authenticated() - Check SSO status",
        "handle_auth_callback(code) - Process Azure callback",
        "get_auth_url() - Generate Azure login URL",
        "logout() - Clear SSO session",
    ]),
    ("Data Structure", [
        "content_data.json structure:",
        "",
        "categories: mfa, vpn, outlook, mobile, software_center, other",
        "Each category has: title, steps[], quiz[]",
        "",
        "user_progress: {user_id: {category: [completed_step_indices]}}",
        "user_profiles: {user_id: {name, email, department}}",
        "quiz_results: {user_id: {category: {score, passed}}}",
        "analytics: {page_views: {}, completions: {}}",
    ]),
    ("Deployment", [
        "Requirements:",
        "pip install streamlit fpdf2 msal",
        "",
        "Run locally:",
        "streamlit run induction.py",
        "",
        "Production:",
        "- Configure Azure AD App Registration",
        "- Set .streamlit/secrets.toml",
        "- Deploy to Streamlit Cloud or container",
    ]),
]

# ========== AZURE SSO GUIDE ==========
sso_sections = [
    ("Prerequisites", [
        "1. Azure AD Tenant with admin access",
        "2. App Registration in Azure Portal",
        "3. Python packages: msal",
        "",
        "Install: pip install msal",
    ]),
    ("Step 1: Azure Portal Configuration", [
        "1.1 Register Application:",
        "- Go to Azure Portal > Azure Active Directory",
        "- App registrations > New registration",
        "- Name: Prysmian Induction Portal",
        "- Redirect URI: http://localhost:8501 (dev) or production URL",
        "- Supported account types: Single tenant",
        "",
        "1.2 Configure Authentication:",
        "- Go to Authentication > Add platform > Web",
        "- Add redirect URIs for dev and production",
        "- Enable ID tokens under Implicit grant",
        "",
        "1.3 Get Credentials:",
        "From Overview, copy:",
        "- Application (client) ID",
        "- Directory (tenant) ID",
        "",
        "From Certificates & secrets > New client secret:",
        "- Client Secret value",
    ]),
    ("Step 2: Streamlit Secrets", [
        "Create .streamlit/secrets.toml:",
        "",
        "[azure]",
        "client_id = YOUR_CLIENT_ID",
        "client_secret = YOUR_CLIENT_SECRET",
        "tenant_id = YOUR_TENANT_ID",
        "redirect_uri = http://localhost:8501",
    ]),
    ("Step 3: Code Integration", [
        "In induction.py, add at the beginning:",
        "",
        "from modules.sso_azure import require_authentication",
        "require_authentication()",
        "",
        "This will:",
        "- Check for Azure callback code in URL",
        "- Redirect to Azure login if not authenticated",
        "- Auto-save user profile from SSO token",
        "- Allow app to continue once authenticated",
    ]),
    ("Step 4: Modify get_user_id()", [
        "In data_manager.py, update get_user_id():",
        "",
        "First check for SSO user:",
        "sso_user = st.session_state.get('sso_user')",
        "if sso_user and sso_user.get('oid'):",
        "    return sso_user['oid']  # Use Azure Object ID",
        "",
        "This ensures consistent user tracking across sessions.",
    ]),
    ("Security Considerations", [
        "1. Never commit secrets.toml - Add to .gitignore",
        "2. Use HTTPS in production - Required for secure OAuth",
        "3. Token expiration - Implement token refresh logic",
        "4. Logout - Add Azure logout URL redirect",
    ]),
    ("Testing", [
        "1. Run locally with dev redirect URI",
        "2. Login with test Azure account",
        "3. Verify profile auto-creation in content_data.json",
        "4. Check progress tracking works with SSO user ID",
    ]),
]

# Generate PDFs
create_doc_pdf("Project Overview", project_sections, "docs/PROJECT_OVERVIEW.pdf")
create_doc_pdf("Azure AD SSO Integration Guide", sso_sections, "docs/AZURE_SSO_INTEGRATION.pdf")

print("\\nAll PDFs generated successfully!")
