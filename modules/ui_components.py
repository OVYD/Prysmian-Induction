import streamlit as st
import os
from modules.data_manager import load_data
from modules.search import search_content
from modules.auth import login_sidebar

MEDIA_DIR = "images"

def inject_custom_css():
    # Initialize session state for dark mode if not present
    # We default to dark mode for the premium feel
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True

    # 1. STRUCTURAL CSS (Applied in BOTH modes)
    structural_css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            html, body, [class*="css"], .stApp, section[data-testid="stSidebar"] {
                font-family: 'Inter', sans-serif !important;
            }
            
            /* CUSTOM HEADER VISIBILITY */
            header[data-testid="stHeader"] {
                background: transparent !important;
                z-index: 1 !important;
            }
            
            /* Hide Decoration Line */
            div[data-testid="stDecoration"] {
                display: none !important;
            }
            
            /* Sidebar width control */
            section[data-testid="stSidebar"] {
                width: 260px !important;
            }
        </style>
    """
    st.markdown(structural_css, unsafe_allow_html=True)

    # 2. THEME CSS
    # For this "Best Version", we rely heavily on the assets/style.css which is tailored for the Prysmian Dark Theme.
    # Even if "dark_mode" toggle is present, we prioritize the premium dark look.
    
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            custom_css = f.read()
            st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)

def render_sidebar():
    st.sidebar.markdown("### Induction Portal")
    
    # --- SEARCH BOX ---
    st.sidebar.markdown("---")
    query = st.sidebar.text_input("🔍 Search Guide...", placeholder="e.g. VPN, Outlook")
    search_results = []
    if query:
        search_results = search_content(query)
        if not search_results:
            st.sidebar.warning("No results found.")
        else:
            st.sidebar.success(f"Found {len(search_results)} matches!")
    
    st.sidebar.markdown("---")
    
    # --- NAVIGATION ---
    data = load_data()
    categories = data.get("categories_list", {})
    
    # --- SORTING LOGIC: USE DICTIONARY ORDER ---
    # We use the order directly from the database (categories_list is an ordered dict in Python 3.7+)
    sorted_names = list(categories.values())
    
    pages = ["🏠 Home"] + sorted_names
    
    # Check for admin
    if st.session_state.get("admin_logged_in", False):
        pages.append("⚙️ Admin Panel")
        
    selection = st.sidebar.radio("Navigation", pages, label_visibility="collapsed")
    
    # --- FOOTER & LOGIN ---
    st.sidebar.markdown("---")
    login_sidebar()
    
    st.sidebar.markdown(
        """
        <div class="sidebar-footer">
            Prysmian Induction App<br>
            <span style="color: #00D2BE; font-weight: bold;">v36.0</span><br>
            <div style="margin-top: 8px; font-size: 10px; opacity: 0.5; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 5px;">
                Created by Dinulescu Cosmin Ovidiu
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    return selection, query, search_results

def render_home_page():
    data = load_data()
    home_content = data.get("home", {})
    
    # 1. Logo Display (Prioritize user selection, then default Prysmian)
    logo_file = home_content.get("logo", "")
    
    # If no custom logo is set in data, try to find the standard project logo
    if not logo_file:
         # Check for common Prysmian logo files in images dir
         potential_logos = ["Prysmian logo positive transparent bckgr.png", "Prysmian_Logo_CMYK_Positive.jpg"]
         for pl in potential_logos:
             if os.path.exists(os.path.join(MEDIA_DIR, pl)):
                 logo_file = pl
                 break
    
    if logo_file:
        logo_path = os.path.join(MEDIA_DIR, logo_file)
        if os.path.exists(logo_path):
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(logo_path, use_container_width=True)
            
    # 2. Welcome Text
    text_content = home_content.get("text", "Welcome to the IT Induction Portal.")
    
    # Ensure High Contrast Title and Centering
    text_content = text_content.replace("# Welcome ", "<h1 style='text-align: center;'>Welcome ")
    
    # Wrap in centered container for the rest of the text
    st.markdown(f"<div style='text-align: center;'>{text_content}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("👈 Please select a guide from the sidebar to get started.")

def render_search_results(results):
    st.title(f"🔍 Search Results")
    st.caption(f"Found {len(results)} items matching your query.")
    
    for res in results:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.subheader(res["title"])
                st.write(res["preview"])
                st.caption(f"Type: {res['type']}")
            with c2:
                if st.button("Go to \u2794", key=f"search_{res['title']}_{res['location']}_{res.get('step_index', 'main')}"):
                    st.query_params["page"] = res["location"]
                    st.rerun()

def render_category_page(category_key):
    data = load_data()
    cat_name = data["categories_list"].get(category_key, "Unknown Category")
    content = data.get(category_key, {"description": "", "steps": []})
    
    st.header(cat_name)
    if content.get("description"):
        st.info(content.get("description", ""))
    
    steps = content.get("steps", [])
    if not steps:
        st.warning("No content available yet.")
        return

    for i, step in enumerate(steps):
        # Determine Title
        step_title = step.get('title', '').strip()
        if not step_title:
            step_title = f"Step {i+1}"
            
        # Premium Step Card Structure
        st.markdown(f"""
        <div class="step-container">
            <div class="step-header">
                <div class="step-number">{i+1}</div>
                <h3>{step_title}</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([1.5, 1])
        
        with c1:
            st.markdown(step.get('text', ''))
        
        with c2:
            media_file = step.get('image')
            video_url = step.get('video_url')
            
            # --- VIDEO HANDLER ---
            if video_url:
                if "sharepoint.com" in video_url or "microsoftstream.com" in video_url:
                    st.info("🔒 Corporate Video")
                    st.caption("Secure SharePoint Content")
                    st.link_button("▶️ Watch on SharePoint", video_url, type="primary")
                else:
                    try:
                        st.video(video_url)
                    except Exception:
                        st.warning("⚠️ Cannot play video inline.")
                        st.link_button("🔗 Open Link", video_url)
            
            # --- IMAGE HANDLER ---
            if media_file:
                 media_path = os.path.join(MEDIA_DIR, media_file)
                 if os.path.exists(media_path):
                     if media_path.lower().endswith(('.mp4', '.mov')):
                         st.video(media_path)
                     else:
                        st.image(media_path, use_container_width=True)
