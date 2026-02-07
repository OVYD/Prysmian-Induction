import streamlit as st
import os
import base64
import time
from modules.data_manager import (
    load_data, save_step_feedback, save_user_progress, load_user_progress, 
    save_bookmark, load_bookmarks, track_page_view, track_completion,
    get_quiz, save_quiz_result, get_quiz_result, get_user_profile,
    get_user_completion_status
)
from modules.search import search_content
from modules.auth import login_sidebar

MEDIA_DIR = "images"



@st.dialog("Zoom", width="large")
def show_image_dialog(image_path):
    st.image(image_path, use_container_width=True)

def render_zoomable_image(image_path, key=None):
    """
    Renders an image that, when clicked, opens a zoom dialog via URL parameter trigger.
    """
    if key is None:
        key = image_path
        
    # --- HIDDEN BUTTON PROXY STRATEGY ---
    # To avoid the "Page Reload" feel of URL params, we use a native st.button.
    # But we want the IMAGE to be the trigger.
    # Solution: Render a button, use JS to hide it, and use JS to click it when image is clicked.
    
    # Unique label we can find with JS
    trigger_label = f"ZOOM_TRIGGER_{key}"
    
    # 1. The Hidden Button (Python handles the click)
    # We place it in a container that we will try to hide/collapse
    if st.button(trigger_label, key=f"btn_proxy_{key}"):
         show_image_dialog(image_path)

    # Convert image to base64
    img_b64 = get_image_base64(image_path)
    if img_b64:
        # 2. The Image Trigger (JS clicks the button above)
        # 3. The JS Cleanup (Hides the button visually)
        
        # We use a script in a component (iframe) to manipulate the parent window
        # The IMAGE is also rendered inside this component so onclick works
        html_with_script = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; }}
                    .zoom-img {{
                        width: 100%;
                        border-radius: 4px;
                        transition: opacity 0.2s;
                        cursor: zoom-in;
                    }}
                    .zoom-img:hover {{
                        opacity: 0.9;
                    }}
                </style>
            </head>
            <body>
                <img class="zoom-img" 
                     src="data:image/png;base64,{img_b64}" 
                     onclick="triggerZoom()">
                
                <script>
                    function triggerZoom() {{
                        // Find and click the hidden button in the parent Streamlit frame
                        const buttons = window.parent.document.querySelectorAll('button');
                        for (const btn of buttons) {{
                            if (btn.innerText === '{trigger_label}') {{
                                btn.click();
                                return;
                            }}
                        }}
                    }}
                    
                    // HIDE the proxy button on load
                    (function() {{
                        const buttons = window.parent.document.querySelectorAll('button');
                        for (const btn of buttons) {{
                            if (btn.innerText === '{trigger_label}') {{
                                btn.style.display = 'none';
                                const parent = btn.closest('.stButton');
                                if (parent) {{
                                    parent.style.display = 'none';
                                }}
                            }}
                        }}
                    }})();
                </script>
            </body>
            </html>
        """
        # Use height proportional to likely image size (auto-sizing is hard in iframes)
        # An estimated 300px height works for most screenshots; could be made dynamic later
        st.components.v1.html(html_with_script, height=350, scrolling=False)

    else:
        # Fallback if base64 fails
        st.image(image_path, use_container_width=True)

@st.cache_data(show_spinner=False)
def get_image_base64(path):
    """Helper to convert image to base64 for HTML embedding"""
    try:
        with open(path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except Exception:
        return None

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
    
    # --- FLOATING HELP BUTTON (TickIT) ---
    tickit_url = "https://teams.microsoft.com/l/app/4bfb8e8b-c798-41f3-abf8-31852c3c3755?source=app-bar-share-entrypoint"
    help_button_html = f"""
    <div class="help-button-container">
        <a href="{tickit_url}" target="_blank" class="help-button">
            💬 Need Help?
        </a>
    </div>
    """
    st.markdown(help_button_html, unsafe_allow_html=True)

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
    
    # --- MOBILE: Auto-close sidebar on navigation ---
    # Inject JavaScript that actually runs using components.html
    import streamlit.components.v1 as components
    
    # This creates an invisible iframe that runs our script
    components.html("""
        <script>
        // Access parent window (Streamlit app)
        const parent = window.parent.document;
        
        // Check if mobile
        if (window.parent.innerWidth <= 768) {
            // Function to close sidebar
            function closeSidebar() {
                // Try multiple selectors for the collapse button
                const selectors = [
                    'button[data-testid="collapsedControl"]',
                    'button[aria-label="Close sidebar"]',
                    'section[data-testid="stSidebar"] button[kind="header"]',
                    'button[data-testid="baseButton-headerNoPadding"]',
                    '.stSidebar button'
                ];
                
                for (const sel of selectors) {
                    const btn = parent.querySelector(sel);
                    if (btn) {
                        btn.click();
                        return true;
                    }
                }
                
                // Fallback: directly manipulate sidebar attribute
                const sidebar = parent.querySelector('section[data-testid="stSidebar"]');
                if (sidebar) {
                    sidebar.setAttribute('aria-expanded', 'false');
                }
                return false;
            }
            
            // Listen for clicks on navigation items
            parent.addEventListener('click', function(e) {
                const target = e.target;
                
                // Check if clicked on radio button, button in sidebar, or link
                const isRadio = target.closest('label[data-baseweb="radio"]');
                const isSidebarButton = target.closest('section[data-testid="stSidebar"] button');
                const isNavLink = target.closest('[data-testid="stSidebarNav"] a');
                
                if (isRadio || isSidebarButton || isNavLink) {
                    // Delay to let Streamlit process, then close
                    setTimeout(closeSidebar, 150);
                }
            }, true);
        }
        </script>
    """, height=0)
    
    # --- SEARCH BOX ---
    st.sidebar.markdown("---")
    
    # Use a counter-based key to force widget recreation when clearing
    if "search_key_counter" not in st.session_state:
        st.session_state.search_key_counter = 0
    
    # Check if we need to clear search (set by navigation buttons)
    if st.session_state.get("clear_search", False):
        st.session_state.clear_search = False
        st.session_state.search_key_counter += 1  # Increment to get new widget
    
    # Text input with dynamic key - changing key creates fresh widget
    query = st.sidebar.text_input(
        "🔍 Search guide...", 
        placeholder="VPN, MFA, Outlook...",
        key=f"search_input_{st.session_state.search_key_counter}"
    )
    
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
        
        # Clear search when navigating
        st.session_state.clear_search = True
        st.session_state.current_search = ""  # Also clear current value
        
        # Update URL
        st.query_params["page"] = new_key
        
        # Clear step and zoom params if switching categories
        for param in ["step", "zoom_target", "uid"]:
            if param in st.query_params:
                del st.query_params[param]

    # 5. Render Widget
    # Note: No 'index' argument used! We rely on 'key' and session_state.
    selection = st.sidebar.radio(
        "Navigation", 
        pages, 
        key="nav_selection", 
        on_change=update_url_callback,
        label_visibility="collapsed"
    )
    
    # --- MY BOOKMARKS SECTION ---
    user_bookmarks = load_bookmarks()
    if user_bookmarks:
        st.sidebar.markdown("---")
        with st.sidebar.expander(f"⭐ My Bookmarks ({len(user_bookmarks)})", expanded=False):
            data = load_data()
            categories = data.get("categories_list", {})
            
            for bm in user_bookmarks:
                # Parse bookmark key: "category_step_index"
                parts = bm.split("_step_")
                if len(parts) != 2:
                    continue
                    
                cat_key, step_idx = parts[0], parts[1]
                cat_name = categories.get(cat_key, cat_key)
                
                # Get step title
                try:
                    step_data = data.get(cat_key, {}).get("steps", [])
                    step_title = step_data[int(step_idx)].get("title", f"Step {int(step_idx) + 1}")
                    if not step_title:
                        step_title = f"Step {int(step_idx) + 1}"
                except:
                    step_title = f"Step {int(step_idx) + 1}"
                
                # Navigation button
                if st.button(f"📌 {step_title[:25]}...", key=f"bm_nav_{bm}", help=f"{cat_name}", use_container_width=True):
                    st.query_params["page"] = cat_key
                    st.query_params["step"] = str(int(step_idx) + 1)
                    st.rerun()
    
    # --- USER PROFILE (Azure SSO) ---
    # User profile is auto-populated from Azure SSO authentication
    # No manual registration needed - email comes from SSO token
    user_profile = get_user_profile()
    if user_profile:
        st.sidebar.success(f"✅ {user_profile.get('name', user_profile.get('email', 'User'))}")
    
    # --- FOOTER & LOGIN ---
    st.sidebar.markdown("---")
    login_sidebar()
    
    st.sidebar.markdown(
        """
        <div class="sidebar-footer">
            Prysmian Induction App<br>
            <span style="color: #00D2BE; font-weight: bold;">1.0 Beta</span><br>
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
                 # Set URL param - the sidebar will sync from this
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
    
    # --- 5. COMPLETION CERTIFICATE ---
    st.markdown("---")
    from modules.certificate import can_get_certificate, generate_certificate
    
    can_cert, cert_msg = can_get_certificate()
    
    c_cert1, c_cert2 = st.columns([2, 1])
    with c_cert1:
        st.subheader("🎓 Completion Certificate")
        if can_cert:
            st.success("Congratulations! You have completed all guides and can download your certificate!")
            if st.button("📜 Generate My Certificate", type="primary"):
                cert_path = generate_certificate()
                if cert_path and os.path.exists(cert_path):
                    with open(cert_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Certificate PDF",
                            data=f,
                            file_name="Prysmian_Induction_Certificate.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.error("Failed to generate certificate.")
        else:
            st.info(cert_msg)
    with c_cert2:
        # Progress summary
        user_status = get_user_completion_status()
        categories = user_status.get("categories", [])
        completed = sum(1 for c in categories if c["guide_complete"])
        total = len(categories)
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: rgba(0,177,64,0.1); border-radius: 12px;">
            <div style="font-size: 48px; font-weight: bold; color: #00B140;">{completed}/{total}</div>
            <div style="font-size: 14px; color: #888;">Guides Completed</div>
        </div>
        """, unsafe_allow_html=True)

def render_search_results(results):
    st.title(f"🔍 Search Results")
    
    # Check for "Best Match" (High Score => Likely a Category Match)
    top_result = results[0] if results else None
    
    if top_result and top_result.get("score", 0) >= 50:
         st.success(f"**Best Match found:** {top_result['title']}")
         
         # Dynamic "Go To Page" Card
         with st.container(border=True):
             c1, c2 = st.columns([3, 1])
             with c1:
                 st.header(top_result['title'])
                 st.write(top_result['preview'])
             with c2:
                 # Big Primary Action Button
                 if st.button(f"Go to {top_result['title']} \u2794", key="s_best_match", type="primary", use_container_width=True):
                     st.session_state.clear_search = True  # Clear search on next run
                     st.query_params["page"] = top_result["location"]
                     st.rerun()
         
         st.markdown("---")
         st.caption(f"Show {len(results)-1} other results")
         
         # Collapsible container for the rest
         with st.expander("See other matches...", expanded=False):
            for res in results[1:]:
                render_search_item(res)
    else:
        st.caption(f"Found {len(results)} items matching your query.")
        for res in results:
            render_search_item(res)

def render_search_item(res):
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.subheader(res["title"])
                st.write(res["preview"])
                st.caption(f"Type: {res['type']}")
            with c2:
                if st.button("Go to \u2794", key=f"search_{res['title']}_{res['location']}_{res.get('step_index', 'main')}"):
                    st.session_state.clear_search = True  # Clear search on next run
                    st.query_params["page"] = res["location"]
                    # If it's a step, add step param? Current search.py logic might need tweak if we want direct step link
                    # For now just going to page is safe.
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
    
    # Track page view for analytics
    track_page_view(category_key)
    
    steps = content.get("steps", [])
    total_steps = len(steps)
    
    # Load progress (try persistent first, then session)
    if f"progress_{category_key}" not in st.session_state:
        st.session_state[f"progress_{category_key}"] = load_user_progress(category_key)
    
    completed_steps = st.session_state.get(f"progress_{category_key}", [])
    completed_count = len(completed_steps)
    progress_pct = int((completed_count / total_steps) * 100) if total_steps > 0 else 0
    
    # Load bookmarks
    user_bookmarks = load_bookmarks()
    
    # --- BREADCRUMBS ---
    st.markdown(f"""
    <div class="breadcrumbs">
        <a href="?page=home">🏠 Home</a> › <span class="current">{cat_name}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # --- HEADER WITH TIME ESTIMATE ---
    # Time estimate: ~2 min per step as default
    estimated_time = content.get("estimated_time", total_steps * 2)
    
    hc1, hc2 = st.columns([4, 1])
    with hc1:
        st.header(cat_name)
        st.caption(f"⏱️ ~{estimated_time} minutes")
    with hc2:
        # Print button using JavaScript - must use components.html for onclick to work
        st.components.v1.html("""
        <button onclick="window.parent.print()" style="
            background: linear-gradient(135deg, #00D2BE, #00B140);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 4px 14px rgba(0, 177, 64, 0.3);
            transition: all 0.2s ease;
        " onmouseover="this.style.transform='translateY(-2px)'" 
           onmouseout="this.style.transform='translateY(0)'">🖨️ Print Guide</button>
        """, height=50)
    
    if content.get("description"):
        st.info(content.get("description", ""))
    
    # --- PROGRESS BAR ---
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-info">
            <span>📊 Progress: {completed_count} of {total_steps} steps</span>
            <span class="progress-pct">{progress_pct}%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {progress_pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
                btn_label = "Completed ✓" if is_completed else "Mark as Done"
                if st.button(btn_label, key=f"done_{category_key}_{i}"):
                    current_prog = st.session_state.get(f"progress_{category_key}", [])
                    if step_id in current_prog:
                        current_prog.remove(step_id)
                    else:
                        current_prog.append(step_id)
                    st.session_state[f"progress_{category_key}"] = current_prog
                    save_user_progress(category_key, current_prog)  # Persist!
                    st.rerun()
            
            with sc2:
                 # Direct Link for sharing
                 st.caption(f"🔗 [Direct Link](?page={category_key}&step={i+1})")
            
            # --- STEP FEEDBACK & BOOKMARK ---
            fc1, fc2, fc3 = st.columns([1, 1, 2])
            with fc1:
                if st.button("👍", key=f"fb_up_{category_key}_{i}", help="This step was helpful"):
                    save_step_feedback(category_key, i, "helpful")
                    st.toast("Thanks for your feedback!", icon="🎉")
            with fc2:
                if st.button("👎", key=f"fb_down_{category_key}_{i}", help="This step needs improvement"):
                    save_step_feedback(category_key, i, "not_helpful")
                    st.toast("Thanks! We'll improve this.", icon="🔧")
            with fc3:
                bookmark_key = f"{category_key}_step_{i}"
                is_bookmarked = bookmark_key in user_bookmarks
                bm_label = "⭐ Bookmarked" if is_bookmarked else "☆ Bookmark"
                if st.button(bm_label, key=f"bm_{category_key}_{i}", help="Save this step for later"):
                    save_bookmark(category_key, i, add=not is_bookmarked)
                    st.toast("Bookmark updated!" if is_bookmarked else "Bookmarked!", icon="⭐")
                    st.rerun()
        
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
            # --- IMAGE HANDLER ---
            if media_file:
                 media_path = os.path.join(MEDIA_DIR, media_file)
                 if os.path.exists(media_path):
                     if media_path.lower().endswith(('.mp4', '.mov')):
                         st.video(media_path)
                     else:
                        # 1. Print-only image (hidden on screen, visible in print)
                        img_b64 = get_image_base64(media_path)
                        if img_b64:
                            st.markdown(f'''
                            <img src="data:image/png;base64,{img_b64}" 
                                 class="print-only-image" 
                                 style="display: none; max-width: 100%; border-radius: 8px;">
                            ''', unsafe_allow_html=True)
                        
                        # 2. Screen-only zoomable image (hidden in print)
                        render_zoomable_image(media_path, key=f"{category_key}_{i}")
    
    # --- CELEBRATION BANNER ---
    if completed_count == total_steps and total_steps > 0:
        track_completion(category_key)  # Track for analytics
        st.balloons()
        st.markdown(f"""
        <div class="celebration-banner">
            <h3>🎉 Congratulations!</h3>
            <p>You have completed all {total_steps} steps in this guide!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # --- QUIZ SECTION ---
        quiz_questions = get_quiz(category_key)
        quiz_result = get_quiz_result(category_key)
        
        if quiz_questions:
            st.markdown("---")
            st.subheader("🧠 Knowledge Check Quiz")
            
            if quiz_result and quiz_result.get("passed"):
                st.success(f"✅ You passed this quiz! Score: {quiz_result['score']}/{quiz_result['total']}")
            else:
                st.info("Answer the questions below to test your knowledge.")
                
                # Quiz form
                with st.form(f"quiz_form_{category_key}"):
                    user_answers = {}
                    
                    for qi, qq in enumerate(quiz_questions):
                        st.markdown(f"**Q{qi+1}: {qq.get('q', 'Question')}**")
                        options = qq.get("answers", [])
                        user_answers[qi] = st.radio(
                            f"Select answer:",
                            options,
                            key=f"quiz_{category_key}_{qi}",
                            label_visibility="collapsed"
                        )
                        st.markdown("")
                    
                    submitted = st.form_submit_button("📝 Submit Quiz", type="primary")
                    
                    if submitted:
                        score = 0
                        for qi, qq in enumerate(quiz_questions):
                            correct_idx = qq.get("correct", 0)
                            options = qq.get("answers", [])
                            if user_answers.get(qi) == options[correct_idx]:
                                score += 1
                        
                        total = len(quiz_questions)
                        passed = score >= (total * 0.7)  # 70% to pass
                        
                        save_quiz_result(category_key, score, total, passed)
                        
                        if passed:
                            st.success(f"🎉 Congratulations! You passed with {score}/{total}!")
                            st.balloons()
                        else:
                            st.error(f"You scored {score}/{total}. You need 70% to pass. Try again!")
                        st.rerun()
    
    # --- FEEDBACK SECTION ---
    st.divider()
    st.caption("Was this guide helpful?")
    fc1, fc2, fc3 = st.columns([1, 1, 5])
    with fc1:
        if st.button("👍 Yes", key=f"fb_yes_{category_key}"):
            st.toast("Thanks for your feedback!", icon="🎉")
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
