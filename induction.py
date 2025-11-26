import streamlit as st
import os
import json
import re
from PIL import Image

# --- BUCATA NOUA: Deschide Browser Automat ---
# Aceasta asigură că atunci când pornești .exe, se deschide pagina
# Doar la prima rulare a scriptului
if "browser_opened" not in st.session_state:
    st.session_state.browser_opened = True
    # Forțăm deschiderea browserului (Streamlit face asta de obicei automat,
    # dar într-un .exe e bine să fii sigur)
# ---------------------------------------------

# --- MODIFICARE PENTRU EXECUTABIL ---
# Salvăm datele în Documentele utilizatorului pentru a nu le pierde
USER_DOCS = os.path.expanduser("~/Documents/InductionApp")
if not os.path.exists(USER_DOCS):
    os.makedirs(USER_DOCS)

DATA_FILE = os.path.join(USER_DOCS, "content_data.json")
# Imaginile ar trebui și ele salvate aici dacă vrei să persiste modificările din Admin
IMAGES_DIR = os.path.join(USER_DOCS, "images") 
# ------------------------------------

# --- 2. DATA MANAGEMENT ---
def load_data():
    base_structure = {
        "home": {"logo": "", "text": "# Welcome!\nSelect a guide from the left."},
        "categories_list": DEFAULT_CATEGORIES,
    }

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(base_structure, f)
        return base_structure
    
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    
    data_modified = False
    
    if "home" not in data:
        data["home"] = base_structure["home"]
        data_modified = True

    if "categories_list" not in data:
        data["categories_list"] = DEFAULT_CATEGORIES
        data_modified = True
        
    current_cats = data["categories_list"]
    for key in current_cats.keys():
        if key not in data:
            data[key] = {"description": "", "steps": []}
            data_modified = True

    if data_modified:
        save_data(data)
        
    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- 3. FRONTEND: USER PAGES ---
def render_category_page(category_key):
    data = load_data()
    cat_name = data["categories_list"].get(category_key, "Unknown Category")
    content = data.get(category_key, {"description": "", "steps": []})
    
    description = content.get("description", "")
    items = content.get("steps", [])
    
    st.header(cat_name)
    
    if category_key == "software_center":
        icon_path = os.path.join(IMAGES_DIR, "software_center.png")
        if os.path.exists(icon_path):
            st.image(icon_path, width=60) 
    
    if description:
        st.info(description)

    st.divider()

    if not items:
        st.warning("📭 No steps added yet. Go to ADMIN PANEL to add content.")
        return

    for index, item in enumerate(items):
        col1, col2 = st.columns([1, 1.5])
        img_path = os.path.join(IMAGES_DIR, item['image'])
        
        # --- MODIFICARE: CUSTOM TITLE ---
        # Verificăm dacă există un titlu personalizat salvat
        custom_title = item.get("title", "").strip()
        
        with col1:
            if custom_title:
                st.subheader(custom_title) # Afișăm titlul tău (ex: "Logare")
            else:
                st.subheader(f"Step {index + 1}") # Fallback la "Step 1"
            
            st.markdown(item.get('text', ''))
        
        with col2:
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.error(f"Image missing: {item['image']}")
        st.divider()

def show_home():
    data = load_data()
    home_content = data.get("home", {})
    
    logo_file = home_content.get("logo", "")
    if logo_file:
        logo_path = os.path.join(IMAGES_DIR, logo_file)
        if os.path.exists(logo_path):
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(logo_path, use_container_width=True)
    
    welcome_text = home_content.get("text", "")
    if welcome_text:
        st.markdown(welcome_text)
    else:
        st.title("🚀 Welcome to the Team!")

# --- 4. BACKEND: ADMIN PANEL ---
def show_admin():
    st.title("⚙️ Admin Dashboard")
    
    tab_cats, tab_create, tab_home = st.tabs(["📂 Manage Content", "➕ Create Category", "🏠 Home Page"])
    
    data = load_data()
    categories = data["categories_list"]

    # --- TAB 1: MANAGE CONTENT ---
    with tab_cats:
        if not categories:
            st.warning("No categories found. Go to 'Create Category' tab.")
        else:
            st.subheader("1. Select Category to Edit")
            cat_display = st.selectbox("Category:", list(categories.values()))
            cat_key = [k for k, v in categories.items() if v == cat_display][0]
            
            current_content = data.get(cat_key, {"description": "", "steps": []})
            current_steps = current_content["steps"]
            current_desc = current_content.get("description", "")

            st.markdown("---")
            
            label_text = f"Intro/Description for {cat_display}:"
            new_desc = st.text_area(label_text, value=current_desc, height=70)
            
            if new_desc != current_desc:
                if cat_key not in data: data[cat_key] = {"description": "", "steps": []}
                data[cat_key]["description"] = new_desc
                save_data(data)
                st.toast("Description Saved!")

            st.markdown("---")

            # Upload Photos
            uploaded_files = st.file_uploader(f"Add photos to '{cat_display}'", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
            
            if uploaded_files and st.button("💾 SAVE PHOTOS"):
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(IMAGES_DIR, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Aici inițializăm titlul gol ("")
                    current_steps.append({
                        "image": uploaded_file.name, 
                        "title": "", 
                        "text": f"**Instructions:** ..."
                    })
                
                if cat_key not in data: data[cat_key] = {"description": "", "steps": []}
                data[cat_key]["steps"] = current_steps
                save_data(data)
                st.success("Saved! You can edit text below.")
                st.rerun()

            # Edit Steps
            if current_steps:
                st.markdown("---")
                st.write("### Edit Steps & Reorder")
                for i, item in enumerate(current_steps):
                    with st.expander(f"Step {i+1}: {item['image']}", expanded=True):
                        c1, c2 = st.columns([1, 3])
                        with c1:
                            img_p = os.path.join(IMAGES_DIR, item['image'])
                            if os.path.exists(img_p):
                                st.image(img_p, width=100)
                        with c2:
                            # --- MODIFICARE: CUSTOM TITLE INPUT ---
                            current_title = item.get("title", "")
                            new_title = st.text_input("Custom Title (Optional - overrides 'Step X'):", value=current_title, key=f"title_{cat_key}_{i}")
                            
                            if new_title != current_title:
                                current_steps[i]['title'] = new_title
                                data[cat_key]["steps"] = current_steps
                                save_data(data)
                            # --------------------------------------

                            new_text = st.text_area("Text (Markdown):", value=item['text'], key=f"txt_{cat_key}_{i}", height=130)
                            if new_text != item['text']:
                                current_steps[i]['text'] = new_text
                                data[cat_key]["steps"] = current_steps
                                save_data(data)
                            
                            col_up, col_down, col_del = st.columns([1,1,2])
                            
                            if col_up.button("⬆️ Up", key=f"up_{cat_key}_{i}") and i > 0:
                                 current_steps[i], current_steps[i-1] = current_steps[i-1], current_steps[i]
                                 save_data(data)
                                 st.rerun()
                            
                            if col_down.button("⬇️ Down", key=f"down_{cat_key}_{i}") and i < len(current_steps)-1:
                                 current_steps[i], current_steps[i+1] = current_steps[i+1], current_steps[i]
                                 save_data(data)
                                 st.rerun()
                            
                            if col_del.button("🗑️ Delete Step", key=f"del_{cat_key}_{i}", type="primary"):
                                current_steps.pop(i)
                                data[cat_key]["steps"] = current_steps
                                save_data(data)
                                st.rerun()
            
            st.markdown("---")
            with st.expander("⚠️ Danger Zone (Delete Category)"):
                st.warning(f"This will delete '{cat_display}' permanently.")
                if st.button(f"🗑️ DELETE CATEGORY '{cat_display}'", type="primary"):
                    del data["categories_list"][cat_key]
                    if cat_key in data:
                        del data[cat_key]
                    save_data(data)
                    st.success("Category Deleted!")
                    st.rerun()

    # --- TAB 2: CREATE CATEGORY ---
    with tab_create:
        st.header("➕ Add New Category")
        st.write("Create a new section in the menu.")
        
        col_new1, col_new2 = st.columns(2)
        with col_new1:
            new_cat_name = st.text_input("Category Name", placeholder="e.g. 🖨️ 7. Printers")
            new_cat_id = st.text_input("Internal ID (Unique)", placeholder="e.g. printers").strip().lower()
            
        if st.button("Create Category"):
            if not new_cat_name or not new_cat_id:
                st.error("Please fill in both fields.")
            elif new_cat_id in categories:
                st.error("This ID already exists. Choose another one.")
            else:
                data["categories_list"][new_cat_id] = new_cat_name
                data[new_cat_id] = {"description": "", "steps": []}
                save_data(data)
                st.success(f"Category '{new_cat_name}' created successfully!")
                st.rerun()

    # --- TAB 3: HOME PAGE ---
    with tab_home:
        st.header("🏠 Home Page Customization")
        home_data = data.get("home", {})
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("1. Company Logo")
            logo_upload = st.file_uploader("Upload Logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
            if logo_upload:
                if st.button("💾 Set as Logo"):
                    logo_path = os.path.join(IMAGES_DIR, logo_upload.name)
                    with open(logo_path, "wb") as f:
                        f.write(logo_upload.getbuffer())
                    home_data["logo"] = logo_upload.name
                    data["home"] = home_data
                    save_data(data)
                    st.success("Logo Updated!")
                    st.rerun()
            current_logo = home_data.get("logo", "")
            if current_logo:
                st.image(os.path.join(IMAGES_DIR, current_logo), width=200, caption="Current Logo")
        
        with col_b:
            st.subheader("2. Welcome Message")
            current_text = home_data.get("text", "")
            new_home_text = st.text_area("Main Content:", value=current_text, height=400)
            if new_home_text != current_text:
                home_data["text"] = new_home_text
                data["home"] = home_data
                save_data(data)
                st.toast("Home page text saved!")

# --- 5. NAVIGATION ---

if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

st.sidebar.title("Navigation")

data_nav = load_data()
current_categories = data_nav.get("categories_list", DEFAULT_CATEGORIES)

def extract_number(name):
    match = re.search(r'(\d+)\.', name)
    if match:
        return int(match.group(1))
    return 999

KEY_TO_DISPLAY = {k: v for k, v in current_categories.items()}
sorted_display_names = sorted(list(current_categories.values()), key=extract_number)

pages_list = ["🏠 Home"] + sorted_display_names

if st.session_state["admin_logged_in"]:
    pages_list.append("⚙️ ADMIN PANEL")

query_params = st.query_params
default_index = 0

if "page" in query_params:
    target_key = query_params["page"]
    if target_key in KEY_TO_DISPLAY:
        target_label = KEY_TO_DISPLAY[target_key]
        if target_label in pages_list:
            default_index = pages_list.index(target_label)

selected_page = st.sidebar.radio("Go to:", pages_list, index=default_index)
st.sidebar.markdown("---")

if not st.session_state["admin_logged_in"]:
    with st.sidebar.expander("Admin Access"):
        if st.button("Login") or st.text_input("Pass", type="password") == "admin123":
            st.session_state["admin_logged_in"] = True
            st.rerun()
else:
    if st.sidebar.button("Logout Admin"):
        st.session_state["admin_logged_in"] = False
        st.rerun()

if selected_page == "🏠 Home":
    show_home()
elif selected_page == "⚙️ ADMIN PANEL":
    show_admin()
else:
    key = [k for k, v in current_categories.items() if v == selected_page][0]
    render_category_page(key)