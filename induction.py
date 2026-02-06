import streamlit as st
import sys
import os

# Fix for Streamlit Cloud "ModuleNotFoundError"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ui_components import inject_custom_css, render_sidebar, render_home_page, render_category_page, render_search_results
from modules.admin import render_admin_panel

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(
    page_title="Induction Portal", 
    page_icon="images/prysmian_icon.png", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. GLOBAL STYLES ---
inject_custom_css()

# --- 3. NAVIGATION & LAYOUT ---
# Initialize session state for admin
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

# Render Sidebar and get selection
selected_page, search_query, search_results = render_sidebar()



# --- 4. CONTENT RENDERING ---

# Priority: Search Results -> Admin -> Specific Page -> Home
if search_query and search_results:
    render_search_results(search_results)
elif selected_page == "⚙️ Admin Panel":
    if st.session_state["admin_logged_in"]:
        render_admin_panel()
    else:
        st.error("Access Denied. Please login.")
elif selected_page == "🏠 Home":
    render_home_page()
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
