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
    # Robust path finding for Streamlit Cloud
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir) # Go up from modules/ to root
    css_path = os.path.join(root_dir, "assets", "style.css")
    
    # Fallback for local CWD execution if needed
    if not os.path.exists(css_path):
        css_path = os.path.join("assets", "style.css")

    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            custom_css = f.read()
            st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)
    else:
        # Debug info if CSS fails to load
        print(f"WARNING: Could not find style.css at {css_path}")

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
    sorted_names = list(categories.values())
    pages = ["🏠 Home"] + sorted_names + ["❓ FAQ / Help"]
    
    # Check for admin
    if st.session_state.get("admin_logged_in", False):
        pages.append("⚙️ Admin Panel")
    
    # --- SYNC LOGIC ---
    # 1. Map Keys <-> Names
    key_to_name = categories.copy()
    key_to_name["home"] = "🏠 Home"
    key_to_name["faq"] = "❓ FAQ / Help"
    key_to_name["admin"] = "⚙️ Admin Panel"
    
    name_to_key = {v: k for k, v in key_to_name.items()}

    # 2. Get current URL state
    current_param_key = st.query_params.get("page", "home")
    target_name_from_url = key_to_name.get(current_param_key, "🏠 Home")
    
    # 3. Ensure Session State matches URL (Source of Truth on Load/Nav)
    # We use a specific key 'nav_selection' for the widget
    if "nav_selection" not in st.session_state:
        st.session_state.nav_selection = target_name_from_url
    else:
        # If URL param implies a different page than what's in state,
        # AND we are not in the middle of a widget interaction (hard to detect directly),
        # generally we trust the URL if it fundamentally disagrees with the *previous* logic.
        # However, to avoid fighting:
        # If the generated key for the CURRENT session selection != URL param,
        # WE UPDATE THE SESSION STATE to match URL. This handles Back Button.
        # But we must skip this if the mismatch is because the USER JUST CLICKED.
        # Streamlit runs the callback BEFORE this script. 
        # So if user clicked, the callback (defined below) ALREADY updated the URL.
        # Thus, by the time we get here, URL and Session State SHOULD match.
        # If they DON'T match here, it means the URL changed externally (Back button).
        
        current_selection_key = name_to_key.get(st.session_state.nav_selection, "home")
        if current_selection_key != current_param_key:
             st.session_state.nav_selection = target_name_from_url

    # 4. Callback to update URL when User Clicks
    def update_url_callback():
        # Get the new selection from state
        new_selection = st.session_state.nav_selection
        new_key = name_to_key.get(new_selection, "home")
        
        # Update URL
        st.query_params["page"] = new_key
        
        # Clear step param if switching categories
        if "step" in st.query_params:
            del st.query_params["step"]

    # 5. Render Widget
    # Note: No 'index' argument used! We rely on 'key' and session_state.
    selection = st.sidebar.radio(
        "Navigation", 
        pages, 
        key="nav_selection", 
        on_change=update_url_callback,
        label_visibility="collapsed"
    )
    
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
    
    # --- 3. QUICK ACTIONS DASHBOARD ---
    st.markdown("### 🚀 Quick Start")
    st.caption("Jump straight to the most useful guides:")
    
    col1, col2, col3 = st.columns(3)
    
    # Define Quick Actions
    actions = [
        {"key": "mfa", "title": "🔐 Setup MFA", "desc": "Configure 2FA for security"},
        {"key": "vpn", "title": "🛡️ Connect VPN", "desc": "Access internal network"},
        {"key": "outlook", "title": "📧 Email Setup", "desc": "Configure Outlook & Sig"}
    ]
    
    # Render Cards
    for i, action in enumerate(actions):
        with [col1, col2, col3][i]:
            # We use a button that spans the width, styled as a card via CSS (roughly)
            # Actually standard buttons are easiest to make functional. 
            # We simulate the card look with HTML and a hidden button or just a button.
            # Let's use standard primary buttons for reliability but styled nicely.
            st.markdown(f"""
            <div class="home-card">
                <h3>{action['title']}</h3>
                <p>{action['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Go to {action['key'].upper()}", key=f"btn_home_{action['key']}", use_container_width=True):
                 st.session_state.nav_selection = data["categories_list"].get(action['key'], "🏠 Home")
                 st.query_params["page"] = action["key"]
                 st.rerun()

    # --- 4. BROWSER EXTENSION ---
    st.markdown("---")
    c_ext1, c_ext2 = st.columns([2, 1])
    with c_ext1:
        st.subheader("🧩 New: Induction Helper Extension")
        st.write("Get quick access to guides directly from your browser toolbar. Includes instant search and deep linking.")
        
        # Download Logic
        ext_path = os.path.join("documents", "InductionExtension.zip")
        if os.path.exists(ext_path):
            with open(ext_path, "rb") as f:
                st.download_button(
                    label="📥 Download Extension (.zip)",
                    data=f,
                    file_name="InductionExtension.zip",
                    mime="application/zip",
                    type="primary"
                )
        else:
            st.warning("Extension package not found.")
            
    with c_ext2:
        st.info("**Installation:**\n1. Download & Unzip.\n2. Go to `chrome://extensions`\n3. Enable 'Developer Mode'.\n4. Click 'Load Unpacked' and select folder.")

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

def render_faq_page():
    st.title("❓ Frequently Asked Questions")
    st.caption("Common solutions for induction problems.")
    
    data = load_data()
    faqs = data.get("faq", [])
    
    if not faqs:
        st.info("No FAQs yet.")
        return

    for i, item in enumerate(faqs):
        with st.expander(f"Q: {item.get('q', 'Question')}"):
            st.write(item.get('a', 'Answer'))

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
        
        # ID for deep linking
        step_id = f"step-{i+1}"
        
        # Check completion status
        is_completed = step_id in st.session_state.get(f"progress_{category_key}", [])
        container_class = "step-container completed" if is_completed else "step-container"
            
        # Premium Step Card Structure with ID
        st.markdown(f"""
        <div id="{step_id}" class="{container_class}">
            <div class="step-header">
                <div class="step-number">{i+1}</div>
                <h3>{step_title}</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([1.5, 1])
        
        with c1:
            st.markdown(step.get('text', ''))
            
            # --- PROGRESS & SHARING ---
            sc1, sc2 = st.columns([1, 1])
            with sc1:
                # MARK AS DONE BUTTON
                btn_label = "✅ Completed" if is_completed else "⭕ Mark as Done"
                if st.button(btn_label, key=f"done_{category_key}_{i}"):
                    current_prog = st.session_state.get(f"progress_{category_key}", [])
                    if step_id in current_prog:
                        current_prog.remove(step_id)
                    else:
                        current_prog.append(step_id)
                    st.session_state[f"progress_{category_key}"] = current_prog
                    st.rerun()
            
            with sc2:
                 # Direct Link for sharing
                 st.caption(f"🔗 [Direct Link](?page={category_key}&step={i+1})")
        
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
    
    # --- FEEDBACK SECTION ---
    st.divider()
    st.caption("Was this guide helpful?")
    fc1, fc2, fc3 = st.columns([1, 1, 5])
    with fc1:
        if st.button("👍 Yes", key=f"fb_yes_{category_key}"):
            st.toast("Thank you for your feedback!", icon="🎉")
             # Ideally we would log this to a file
    with fc2:
        if st.button("👎 No", key=f"fb_no_{category_key}"):
            st.toast("We'll try to improve.", icon="🔧")
    
    # --- AUTO-SCROLL SCRIPT ---
    # Injects JS to scroll to the specific step if 'step' param is in URL
    st.components.v1.html(
        """
        <script>
            try {
                // Wait small delay to ensure rendering
                setTimeout(function() {
                    const urlParams = new URLSearchParams(window.parent.location.search);
                    const step = urlParams.get('step');
                    if (step) {
                        const elementId = 'step-' + step;
                        // Search in parent frame (Streamlit structure)
                        const elements = window.parent.document.querySelectorAll('#' + elementId);
                        if (elements.length > 0) {
                            elements[0].scrollIntoView({behavior: "smooth", block: "center"});
                        }
                    }
                }, 500);
            } catch(e) {
                console.log("Auto-scroll error:", e);
            }
        </script>
        """, 
        height=0
    )
