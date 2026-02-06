import streamlit as st
import streamlit.components.v1 as components
import os
import json
import re
import datetime
import hashlib
from PIL import Image
import urllib.parse 

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="Induction Portal", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

MEDIA_DIR = "images"
DATA_FILE = "content_data.json"

# --- THEME CSS INJECTION ---
def apply_theme(dark_mode):
    if dark_mode:
        st.markdown("""
            <style>
                /* Dark Mode Overrides */
                .stApp {
                    background-color: #0E1117;
                    color: #FAFAFA;
                }
                .sidebar-footer {
                    background-color: transparent !important;
                    color: #aaa !important;
                }
                .stTextInput > div > div > input {
                    color: #FAFAFA;
                    background-color: #262730;
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                /* Light Mode Overrides */
                .stApp {
                    background-color: #FFFFFF;
                    color: #31333F;
                }
                .sidebar-footer {
                    background-color: transparent !important;
                    color: #808495 !important;
                }
            </style>
        """, unsafe_allow_html=True)

# --- CSS: LOCK SIDEBAR & SEAMLESS FOOTER ---
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            width: 260px !important;
        }
        div[data-testid="stSidebar"] {
            min-width: 260px !important;
            max-width: 260px !important;
        }
        div[data-testid="stSidebar"] > div:nth-child(2) {
            display: none; 
        }
        .sidebar-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 260px;
            padding: 15px;
            text-align: center;
            font-size: 11px;
            z-index: 100;
            pointer-events: none;
        }
        div[data-testid="stSidebarUserContent"] {
            padding-bottom: 50px;
        }
    </style>
""", unsafe_allow_html=True)

# --- DEFAULT CATEGORIES ---
DEFAULT_CATEGORIES = {
    "mfa": "🔐 1. MFA (Microsoft 2FA)",
    "vpn": "🛡️ 2. VPN Config",
    "outlook": "📧 3. Outlook & Email",
    "mobile": "📱 4. Mobile APN",
    "software_center": "💿 5. Software Center",
    "other": "📚 6. Other Tutorials"
}

if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

# --- SECURITY UTILS ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verify_password(stored_hash, provided_password):
    return stored_hash == hashlib.sha256(str.encode(provided_password)).hexdigest()

# --- 2. DATA MANAGEMENT ---
def load_data():
    base_structure = {
        "home": {"logo": "", "text": "# Welcome!\nSelect a guide from the left."},
        "categories_list": DEFAULT_CATEGORIES,
        "system_logs": [],
        "admins": {}
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
    if "system_logs" not in data:
        data["system_logs"] = []
        data_modified = True
    if "admins" not in data:
        data["admins"] = {}
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
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"CRITICAL ERROR SAVING DATA: {e}")

def log_event(message, level="INFO"):
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {"system_logs": []}
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}"
        
        if "system_logs" not in data: data["system_logs"] = []
        data["system_logs"].insert(0, entry)
        if len(data["system_logs"]) > 100:
            data["system_logs"] = data["system_logs"][:100]
            
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

# --- 3. FRONTEND: USER PAGES ---
def render_category_page(category_key):
    data = load_data()
    cat_name = data["categories_list"].get(category_key, "Unknown Category")
    content = data.get(category_key, {"description": "", "steps": []})
    
    description = content.get("description", "")
    items = content.get("steps", [])
    
    # HEADER CU SHARE
    c_head1, c_head2 = st.columns([4, 1])
    with c_head1:
        st.header(cat_name)
    with c_head2:
        with st.popover("📤 Share"):
            base_url = "https://prysmian-induction.streamlit.app/" 
            share_link = f"{base_url}?page={category_key}"
            
            st.markdown("##### Share this guide")
            subject = urllib.parse.quote(f"Induction Guide: {cat_name}")
            body = urllib.parse.quote(f"Hello,\n\nCheck out this guide for {cat_name}:\n{share_link}\n\nBest regards.")
            mailto_link = f"mailto:?subject={subject}&body={body}"
            st.link_button("📧 Send via Email", mailto_link)
            st.divider()
            st.caption("🔗 Direct Link")
            st.code(share_link, language=None)
            st.divider()
            st.caption("💻 Embed Code (SharePoint/Teams)")
            embed_code = f'<iframe src="{share_link}" width="100%" height="800px" style="border:none;"></iframe>'
            st.code(embed_code, language="html")
    
    if category_key == "software_center":
        icon_path = os.path.join(MEDIA_DIR, "software_center.png")
        if os.path.exists(icon_path):
            st.image(icon_path, width=60) 
    
    if description:
        st.info(description)

    st.divider()

    if not items:
        st.warning("📭 No content added yet.")
        return

    for index, item in enumerate(items):
        col1, col2 = st.columns([1, 1.5])
        
        media_file = item.get('image', '')
        video_url = item.get('video_url') or item.get('youtube', '')
        step_icon = item.get('icon', '')
        
        media_path = os.path.join(MEDIA_DIR, media_file)
        custom_title = item.get("title", "").strip()
        
        # --- FIX: Ascundem titlul "Video Tutorial" daca nu exista video ---
        if custom_title == "Video Tutorial" and not video_url:
            custom_title = "" 
        # -----------------------------------------------------------------

        with col1:
            if custom_title:
                st.subheader(custom_title)
            else:
                st.subheader(f"Step {index + 1}")
            
            if step_icon:
                icon_fpath = os.path.join(MEDIA_DIR, step_icon)
                if os.path.exists(icon_fpath):
                    st.image(icon_fpath, width=64)
            
            st.markdown(item.get('text', ''))
        
        with col2:
            if video_url:
                if "sharepoint.com" in video_url or "microsoftstream.com" in video_url:
                    st.info("🔒 Corporate Video (Secured)")
                    st.caption("This video requires SharePoint login.")
                    st.link_button("▶️ Watch Video on SharePoint", video_url, type="primary")
                else:
                    try:
                        st.video(video_url)
                    except Exception:
                        st.warning("⚠️ Cannot play video inline.")
                        st.link_button("🔗 Open Link", video_url)
            
            if video_url and media_file and os.path.exists(media_path):
                st.write("---")

            if media_file and os.path.exists(media_path):
                if media_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    st.video(media_path)
                else:
                    st.image(media_path, width="stretch")
            
            if not video_url and not (media_file and os.path.exists(media_path)):
                 pass
                
        st.divider()

def show_home():
    data = load_data()
    home_content = data.get("home", {})
    
    c_h1, c_h2 = st.columns([4, 1])
    with c_h2:
        with st.popover("📤 Share App"):
            base_url = "https://prysmian-induction.streamlit.app/"
            st.markdown("##### Share Application")
            subject = urllib.parse.quote("IT Induction Portal")
            body = urllib.parse.quote(f"Hello,\n\nAccess the IT Induction Portal here:\n{base_url}")
            st.link_button("📧 Email Link", f"mailto:?subject={subject}&body={body}")
            st.caption("🔗 Link")
            st.code(base_url, language=None)
    
    logo_file = home_content.get("logo", "")
    if logo_file:
        logo_path = os.path.join(MEDIA_DIR, logo_file)
        if os.path.exists(logo_path):
            with c_h1:
               pass
            c_center = st.container()
            with c_center:
                 col_l, col_c, col_r = st.columns([1, 2, 1])
                 with col_c:
                     st.image(logo_path, width="stretch")
    
    welcome_text = home_content.get("text", "")
    if welcome_text:
        st.markdown(welcome_text)
    else:
        st.title("🚀 Welcome to the Team!")

# --- 4. BACKEND: ADMIN PANEL ---
def show_admin():
    st.title("⚙️ Admin Dashboard")
    
    tab_cats, tab_create, tab_home, tab_users, tab_logs = st.tabs([
        "📂 Manage Content", 
        "➕ Create Category", 
        "🏠 Home Page", 
        "👥 Manage Team", 
        "📋 System Logs"
    ])
    
    data = load_data()
    categories = data["categories_list"]

    with tab_cats:
        if not categories:
            st.warning("No categories found.")
        else:
            st.subheader("1. Select Category")
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
            st.subheader("2. Add Content")
            
            # --- MENIU FLEXIBIL DE ADAUGARE (NOU v30) ---
            add_mode = st.radio("Select Content Type:", 
                ["📤 Quick Media Upload", "🔗 Quick Video Link", "✨ Custom Step (Advanced)"], 
                horizontal=True,
                label_visibility="collapsed"
            )

            # MOD 1: UPLOAD RAPID (BULK)
            if add_mode == "📤 Quick Media Upload":
                st.caption("Upload multiple images or videos instantly.")
                uploaded_files = st.file_uploader(
                    f"Choose files:", 
                    type=['png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'], 
                    accept_multiple_files=True
                )
                
                if uploaded_files and st.button("💾 Add Media Steps"):
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(MEDIA_DIR, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        ftype = "Video" if uploaded_file.name.endswith(('.mp4', '.mov')) else "Image"
                        current_steps.append({
                            "image": uploaded_file.name, "title": "", "video_url": "", "icon": "",
                            "text": f"**Instructions:** Watch the {ftype} above..."
                        })
                    
                    if cat_key not in data: data[cat_key] = {"description": "", "steps": []}
                    data[cat_key]["steps"] = current_steps
                    save_data(data)
                    log_event(f"Added files to {cat_key}")
                    st.success("Steps Added!")
                    st.rerun()
            
            # MOD 2: LINK RAPID
            elif add_mode == "🔗 Quick Video Link":
                st.caption("Add a step with a YouTube or SharePoint link.")
                video_input = st.text_input("Video URL:")
                if st.button("➕ Add Link Step"):
                    if video_input:
                        current_steps.append({
                            "image": "", "title": "Video Tutorial", "video_url": video_input, "icon": "",
                            "text": "**Instructions:** Watch the video..."
                        })
                        if cat_key not in data: data[cat_key] = {"description": "", "steps": []}
                        data[cat_key]["steps"] = current_steps
                        save_data(data)
                        log_event(f"Added URL step to {cat_key}")
                        st.success("Step Added!")
                        st.rerun()

            # MOD 3: CREATOR AVANSAT (CUSTOM)
            elif add_mode == "✨ Custom Step (Advanced)":
                with st.container(border=True):
                    st.info("Create a mixed step: Text + Title + Media (Optional)")
                    
                    c_title, c_icon = st.columns([3, 1])
                    with c_title:
                        new_step_title = st.text_input("Step Title:", placeholder="e.g. 1. Open Software Center")
                    with c_icon:
                        new_step_icon = st.file_uploader("Icon (Optional):", type=['png', 'jpg'])
                    
                    new_step_text = st.text_area("Description / Text:", placeholder="Enter step instructions here...")
                    
                    st.write("**Attach Media (Choose one):**")
                    tab_file, tab_url = st.tabs(["📂 File Upload", "🔗 Video URL"])
                    
                    with tab_file:
                        new_step_file = st.file_uploader("Image/Video:", type=['png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'])
                    with tab_url:
                        new_step_url = st.text_input("Or Video Link:", placeholder="https://...")

                    if st.button("➕ Create Custom Step", type="primary"):
                        # Validare simpla: Sa existe macar ceva
                        if not new_step_title and not new_step_text and not new_step_file and not new_step_url:
                             st.error("Please add at least some content (Title, Text, or Media).")
                        else:
                            # Construim obiectul pasului
                            step_data = {
                                "title": new_step_title,
                                "text": new_step_text,
                                "icon": "",
                                "image": "",
                                "video_url": ""
                            }
                            
                            # Salvare Icon
                            if new_step_icon:
                                icon_path = os.path.join(MEDIA_DIR, new_step_icon.name)
                                with open(icon_path, "wb") as f: f.write(new_step_icon.getbuffer())
                                step_data["icon"] = new_step_icon.name
                                
                            # Salvare Media (Prioritate: Fisier > URL)
                            if new_step_file:
                                f_path = os.path.join(MEDIA_DIR, new_step_file.name)
                                with open(f_path, "wb") as f: f.write(new_step_file.getbuffer())
                                step_data["image"] = new_step_file.name
                            elif new_step_url:
                                step_data["video_url"] = new_step_url
                                
                            current_steps.append(step_data)
                            
                            if cat_key not in data: data[cat_key] = {"description": "", "steps": []}
                            data[cat_key]["steps"] = current_steps
                            save_data(data)
                            log_event(f"Added custom step to {cat_key}")
                            st.success("Custom Step Created!")
                            st.rerun()

            if current_steps:
                st.markdown("---")
                st.write("### Edit Content & Reorder")
                for i, item in enumerate(current_steps):
                    # --- NOU: Etichete Inteligente pentru Expander ---
                    label_parts = []
                    if item.get("title"): label_parts.append(f"📌 {item['title']}")
                    if item.get("image"): label_parts.append("🖼️ Media")
                    if item.get("video_url"): label_parts.append("🎥 Video")
                    if not label_parts and item.get("text"): label_parts.append("📝 Text Only")
                    
                    header_label = f"Step {i+1}: " + " | ".join(label_parts) if label_parts else f"Step {i+1}: (Empty)"
                    # ------------------------------------------------
                    
                    with st.expander(header_label, expanded=True):
                        c1, c2 = st.columns([1, 3])
                        with c1:
                            current_icon = item.get('icon', '')
                            if current_icon:
                                icon_path = os.path.join(MEDIA_DIR, current_icon)
                                if os.path.exists(icon_path):
                                    st.image(icon_path, width=50, caption="Icon")
                            st.write("---")
                            preview_url = item.get('video_url')
                            if preview_url:
                                if "sharepoint" in preview_url: 
                                    st.info("Link")
                                else: 
                                    try:
                                        st.video(preview_url)
                                    except Exception:
                                        st.warning("⚠️ Invalid Video URL")
                                        st.caption(preview_url)

                            if item.get('image'):
                                fpath = os.path.join(MEDIA_DIR, item['image'])
                                if os.path.exists(fpath):
                                    if fpath.lower().endswith(('.mp4', '.mov')): st.video(fpath)
                                    else: st.image(fpath, width=100)
                        
                        with c2:
                            current_title = item.get("title", "")
                            new_title = st.text_input("Custom Title:", value=current_title, key=f"title_{cat_key}_{i}")
                            if new_title != current_title:
                                current_steps[i]['title'] = new_title
                                data[cat_key]["steps"] = current_steps
                                save_data(data)

                            st.caption("🖼️ Step Icon:")
                            new_icon = st.file_uploader("Icon:", type=['png', 'jpg'], key=f"icon_up_{cat_key}_{i}")
                            if new_icon:
                                fpath = os.path.join(MEDIA_DIR, new_icon.name)
                                with open(fpath, "wb") as f: f.write(new_icon.getbuffer())
                                current_steps[i]['icon'] = new_icon.name
                                data[cat_key]["steps"] = current_steps
                                save_data(data)
                                st.rerun()

                            st.caption("📂 Main Media:")
                            new_upload = st.file_uploader("Replace:", type=['png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'], key=f"reup_{cat_key}_{i}")
                            if new_upload:
                                fpath = os.path.join(MEDIA_DIR, new_upload.name)
                                with open(fpath, "wb") as f: f.write(new_upload.getbuffer())
                                current_steps[i]['image'] = new_upload.name
                                data[cat_key]["steps"] = current_steps
                                save_data(data)
                                st.rerun()

                            current_video_url = item.get("video_url") or item.get("youtube", "")
                            new_video_url = st.text_input("Video URL:", value=current_video_url, key=f"vid_{cat_key}_{i}")
                            if new_video_url != current_video_url:
                                current_steps[i]['video_url'] = new_video_url
                                data[cat_key]["steps"] = current_steps
                                save_data(data)
                                st.rerun()

                            new_text = st.text_area("Text:", value=item['text'], key=f"txt_{cat_key}_{i}", height=100)
                            if new_text != item['text']:
                                current_steps[i]['text'] = new_text
                                data[cat_key]["steps"] = current_steps
                                save_data(data)
                            
                            col_up, col_down, col_del = st.columns([1,1,2])
                            if col_up.button("⬆️", key=f"up_{cat_key}_{i}") and i > 0:
                                 current_steps[i], current_steps[i-1] = current_steps[i-1], current_steps[i]
                                 save_data(data)
                                 st.rerun()
                            if col_down.button("⬇️", key=f"down_{cat_key}_{i}") and i < len(current_steps)-1:
                                 current_steps[i], current_steps[i+1] = current_steps[i+1], current_steps[i]
                                 save_data(data)
                                 st.rerun()
                            if col_del.button("🗑️ Delete", key=f"del_{cat_key}_{i}", type="primary"):
                                current_steps.pop(i)
                                data[cat_key]["steps"] = current_steps
                                save_data(data)
                                log_event(f"Deleted step in {cat_key}")
                                st.rerun()
            
            st.markdown("---")
            with st.expander("⚠️ Danger Zone"):
                if st.button(f"🗑️ DELETE CATEGORY '{cat_display}'", type="primary"):
                    try:
                        del data["categories_list"][cat_key]
                        if cat_key in data: del data[cat_key]
                        save_data(data)
                        log_event(f"Deleted CATEGORY {cat_display}", "WARNING")
                        st.success("Deleted!")
                        st.rerun()
                    except Exception as e:
                        log_event(f"Error deleting: {e}", "ERROR")

    with tab_create:
        st.header("➕ Add New Category")
        col_new1, col_new2 = st.columns(2)
        with col_new1:
            new_cat_name = st.text_input("Category Name", placeholder="e.g. 🖨️ 7. Printers")
            new_cat_id = st.text_input("Internal ID (Unique)", placeholder="e.g. printers").strip().lower()
            
        if st.button("Create Category"):
            if new_cat_id in categories: st.error("ID exists.")
            else:
                data["categories_list"][new_cat_id] = new_cat_name
                data[new_cat_id] = {"description": "", "steps": []}
                save_data(data)
                st.success(f"Created!")
                st.rerun()

    with tab_home:
        st.header("🏠 Home Page")
        home_data = data.get("home", {})
        col_a, col_b = st.columns(2)
        with col_a:
            logo_upload = st.file_uploader("Upload Logo", type=['png', 'jpg'])
            if logo_upload and st.button("💾 Set Logo"):
                logo_path = os.path.join(MEDIA_DIR, logo_upload.name)
                with open(logo_path, "wb") as f: f.write(logo_upload.getbuffer())
                home_data["logo"] = logo_upload.name
                data["home"] = home_data
                save_data(data)
                st.rerun()
            if home_data.get("logo"): st.image(os.path.join(MEDIA_DIR, home_data.get("logo")), width=200)
        with col_b:
            current_text = home_data.get("text", "")
            new_home_text = st.text_area("Welcome Message:", value=current_text, height=400)
            if new_home_text != current_text:
                home_data["text"] = new_home_text
                data["home"] = home_data
                save_data(data)
                st.toast("Saved!")

    with tab_users:
        st.header("👥 Manage Team Access")
        st.subheader("Create New Admin")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            new_user = st.text_input("Username:")
        with col_u2:
            new_pass = st.text_input("Password:", type="password")
            
        if st.button("Add User"):
            if new_user and new_pass:
                if new_user == "admin":
                    st.error("Cannot overwrite Master Admin.")
                else:
                    if "admins" not in data: data["admins"] = {}
                    data["admins"][new_user] = hash_password(new_pass)
                    save_data(data)
                    log_event(f"Created admin user: {new_user}")
                    st.success(f"User {new_user} created!")
                    st.rerun()
            else:
                st.error("Please fill both fields.")
        
        st.divider()
        st.subheader("Existing Admins")
        admins = data.get("admins", {})
        if admins:
            for user in list(admins.keys()):
                c1, c2 = st.columns([3, 1])
                with c1: st.write(f"👤 **{user}**")
                with c2:
                    if st.button(f"🗑️ Remove", key=f"del_user_{user}"):
                        del data["admins"][user]
                        save_data(data)
                        log_event(f"Removed admin user: {user}")
                        st.rerun()
        else:
            st.info("No additional admins.")

    with tab_logs:
        st.header("📋 System Logs")
        if st.button("🗑️ Clear Logs"):
            data["system_logs"] = []
            save_data(data)
            st.rerun()
        logs = data.get("system_logs", [])
        if logs: st.text_area("History:", value="\n".join(logs), height=400, disabled=True)
        else: st.write("No logs.")

# --- 5. NAVIGATION ---
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

st.sidebar.title("Navigation")

data_nav = load_data()
current_categories = data_nav.get("categories_list", DEFAULT_CATEGORIES)

def extract_number(name):
    match = re.search(r'(\d+)\.', name)
    if match: return int(match.group(1))
    return 999

KEY_TO_DISPLAY = {k: v for k, v in current_categories.items()}
DISPLAY_TO_KEY = {v: k for k, v in current_categories.items()}
sorted_display_names = sorted(list(current_categories.values()), key=extract_number)

pages_list = ["🏠 Home"] + sorted_display_names

# --- ADMIN HIDDEN ---
if st.session_state["admin_logged_in"]:
    pages_list.append("⚙️ ADMIN PANEL")

query_params = st.query_params
default_index = 0
target_key = query_params.get("page", None)
if target_key:
    if target_key in KEY_TO_DISPLAY:
        target_label = KEY_TO_DISPLAY[target_key]
        if target_label in pages_list:
            default_index = pages_list.index(target_label)
    elif target_key == "home":
        default_index = 0
    elif target_key == "admin" and st.session_state["admin_logged_in"]:
        default_index = pages_list.index("⚙️ ADMIN PANEL")

def on_menu_change():
    selection = st.session_state.menu_selection
    if selection == "🏠 Home": st.query_params["page"] = "home"
    elif selection == "⚙️ ADMIN PANEL": st.query_params["page"] = "admin"
    else:
        key = DISPLAY_TO_KEY.get(selection)
        if key: st.query_params["page"] = key

selected_page = st.sidebar.radio("Go to:", pages_list, index=default_index, key="menu_selection", on_change=on_menu_change)

st.sidebar.markdown("---")

# --- DARK MODE TOGGLE (NOU) ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True  # Default Dark Mode

# Buton Toggle cu salvare stare
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

if dark_mode != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_mode
    st.rerun()

# Aplicam tema
apply_theme(st.session_state.dark_mode)

# --- FOOTER ---
st.sidebar.markdown('<div style="margin-top: 50px;"></div>', unsafe_allow_html=True)
st.sidebar.markdown(
    """
    <div class="sidebar-footer">
        Created by Dinulescu Cosmin Ovidiu<br>
        v30.0 - Dark/Light
    </div>
    """,
    unsafe_allow_html=True
)

# --- LOGIN JOS ---
if not st.session_state["admin_logged_in"]:
    with st.sidebar.expander("Admin Login", expanded=False):
        username_in = st.text_input("Username")
        password_in = st.text_input("Password", type="password")
        if st.button("Login"):
            success = False
            try:
                master_pass = st.secrets["passwords"]["admin_password"]
                if username_in == "admin" and password_in == master_pass:
                    success = True
            except: pass 
            if not success:
                admins = data_nav.get("admins", {})
                if username_in in admins and verify_password(admins[username_in], password_in):
                    success = True
            
            if success:
                st.session_state["admin_logged_in"] = True
                log_event(f"Admin login: {username_in}")
                st.query_params["page"] = "admin"
                st.rerun()
            else:
                st.error("Invalid credentials")
else:
    if st.sidebar.button("Logout"):
        st.session_state["admin_logged_in"] = False
        st.query_params["page"] = "home"
        st.rerun()

if selected_page == "⚙️ ADMIN PANEL":
    if st.session_state["admin_logged_in"]:
        show_admin()
    else:
        st.title("🔒 Access Denied")
        st.warning("Please login using the sidebar menu.")
elif selected_page == "🏠 Home":
    show_home()
else:
    key = [k for k, v in current_categories.items() if v == selected_page][0]
    render_category_page(key)