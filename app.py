import streamlit as st
import os
from modules.ui_components import inject_custom_css, render_sidebar, render_home_page, render_category_page, render_search_results, render_faq_page, get_image_base64
from modules.data_manager import load_data


# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(
    page_title="Induction Portal", 
    page_icon="images/prysmian_icon.png", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. GLOBAL STYLES ---
inject_custom_css()
 
# --- PRELOADER (CACHE WARMING) ---
if "preloaded" not in st.session_state:
    data = load_data()
    # Invisibly preload images into cache
    # This runs only once per session
    for cat_key, content in data.items():
        if isinstance(content, dict) and "steps" in content:
            for step in content["steps"]:
                if "image" in step and step["image"]:
                     # Just calling this populates the @st.cache_data
                     get_image_base64(os.path.join("images", step["image"]))
    
    # Also preload logo
    if "home" in data and "logo" in data["home"] and data["home"]["logo"]:
         get_image_base64(os.path.join("images", data["home"]["logo"]))
         
    st.session_state.preloaded = True

# --- 3. NAVIGATION & LAYOUT ---
# Initialize session state for admin
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

# Render Sidebar and get selection
selected_page, search_query, search_results = render_sidebar()



# --- 4. CONTENT RENDERING ---

# Priority: Search Results -> Admin -> FAQ -> Specific Page -> Home
if search_query and search_results:
    render_search_results(search_results)
elif selected_page == "⚙️ Admin Panel":
    if st.session_state["admin_logged_in"]:
        render_admin_panel()
    else:
        st.error("Access Denied. Please login.")
elif selected_page == "🏠 Home":
    render_home_page()
elif selected_page == "❓ FAQ / Help":
    render_faq_page()
else:
    # Extract category key from name (or map it)
    # The sidebar returns the Full Name (e.g. "🔐 1. MFA...")
    # We need to find the key for it.
    from modules.data_manager import load_data
    data = load_data()
    categories = data.get("categories_list", {})
    
    # Reverse lookup
    found_key = None
    for k, v in categories.items():
        if v == selected_page:
            found_key = k
            break
            
    if found_key:
        render_category_page(found_key)
    else:
        st.error("Page not found.")


