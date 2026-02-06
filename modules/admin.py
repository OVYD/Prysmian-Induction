import streamlit as st
import os
from modules.data_manager import load_data, save_data, log_event
from modules.auth import hash_password

MEDIA_DIR = "images"

def render_admin_panel():
    st.title("⚙️ Admin Dashboard")
    
    tab_cats, tab_reorder, tab_create, tab_home, tab_users, tab_logs = st.tabs([
        "📂 Manage Content", 
        "⇄ Reorder Menu",
        "➕ Create Category", 
        "🏠 Home Page", 
        "👥 Manage Users", 
        "📋 logs"
    ])
    
    data = load_data()
    categories = data["categories_list"]

    # --- TAB: REORDER MENU ---
    with tab_reorder:
        st.header("⇄ Reorder Categories")
        st.info("Move categories up or down. The sidebar will update instantly.")
        
        # Get list of keys in current order
        current_keys = list(categories.keys())
        
        # Iterate to draw controls
        for i, key in enumerate(current_keys):
            with st.container(border=True):
                c_name, c_up, c_down = st.columns([4, 1, 1])
                
                # Display & Rename
                current_name = categories[key]
                new_name = c_name.text_input(f"Name for ID '{key}':", value=current_name, key=f"rename_{key}")
                
                if new_name != current_name:
                    data["categories_list"][key] = new_name
                    save_data(data)
                    st.rerun()

                # Button UP
                if c_up.button("⬆️", key=f"cat_up_{i}", disabled=(i==0)):
                    current_keys[i], current_keys[i-1] = current_keys[i-1], current_keys[i]
                    new_cats = {k: data["categories_list"][k] for k in current_keys}
                    data["categories_list"] = new_cats
                    save_data(data)
                    st.rerun()
                
                # Button DOWN
                if c_down.button("⬇️", key=f"cat_down_{i}", disabled=(i==len(current_keys)-1)):
                    current_keys[i], current_keys[i+1] = current_keys[i+1], current_keys[i]
                    new_cats = {k: data["categories_list"][k] for k in current_keys}
                    data["categories_list"] = new_cats
                    save_data(data)
                    st.rerun()

    # --- TAB 1: MANAGE CONTENT ---
    with tab_cats:
        if not categories:
            st.warning("No categories found.")
        else:
            col_sel, col_del = st.columns([3,1])
            with col_sel:
                cat_display = st.selectbox("Select Category to Edit:", list(categories.values()))
            
            cat_key = [k for k, v in categories.items() if v == cat_display][0]
            
            # --- DANGER ZONE (Delete Category) ---
            with col_del:
                with st.popover("🗑️ Delete"):
                    st.warning(f"Delete '{cat_display}'?")
                    if st.button("Yes, Delete Category"):
                        del data["categories_list"][cat_key]
                        if cat_key in data: del data[cat_key]
                        save_data(data)
                        st.success("Deleted!")
                        st.rerun()

            current_content = data.get(cat_key, {"description": "", "steps": []})
            current_steps = current_content.get("steps", [])
            
            # Category Description
            st.subheader("Intro / Description")
            new_desc = st.text_area("Category Description:", value=current_content.get("description", ""), height=70)
            if new_desc != current_content.get("description"):
                if cat_key not in data: data[cat_key] = {"description": "", "steps": []}
                data[cat_key]["description"] = new_desc
                save_data(data)

            st.markdown("---")
            
            # --- ADVANCED CONTENT CREATOR ---
            st.subheader("Add New Content")
            add_mode = st.radio("Content Type:", 
                ["📤 Quick Upload (Images/Videos)", "🔗 Quick Video Link", "✨ Custom Step (Advanced)"], 
                horizontal=True,
                label_visibility="collapsed"
            )

            # MODE 1: BULK UPLOAD
            if add_mode == "📤 Quick Upload (Images/Videos)":
                st.caption("Upload multiple media files to create steps strictly for them.")
                uploaded_files = st.file_uploader("Choose files:", type=['png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'], accept_multiple_files=True)
                
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
                    st.success("Steps Added!")
                    st.rerun()

            # MODE 2: QUICK LINK
            elif add_mode == "🔗 Quick Video Link":
                video_input = st.text_input("Paste Video URL (YouTube/SharePoint):")
                if st.button("➕ Add Link Step") and video_input:
                    current_steps.append({
                        "image": "", "title": "Video Tutorial", "video_url": video_input, "icon": "",
                        "text": "**Instructions:** Watch the video..."
                    })
                    if cat_key not in data: data[cat_key] = {"description": "", "steps": []}
                    data[cat_key]["steps"] = current_steps
                    save_data(data)
                    st.success("Added!")
                    st.rerun()

            # MODE 3: CUSTOM STEP
            elif add_mode == "✨ Custom Step (Advanced)":
                with st.container(border=True):
                    c_title, c_icon = st.columns([3, 1])
                    with c_title:
                        ns_title = st.text_input("Title:", placeholder="e.g. 1. Connect VPN")
                    with c_icon:
                        ns_icon = st.file_uploader("Icon (Opt):", type=['png', 'jpg'])
                    
                    ns_text = st.text_area("Description:", placeholder="Step details...")
                    
                    st.write("**Attach Media:**")
                    t_f, t_u = st.tabs(["📂 File", "🔗 URL"])
                    with t_f: ns_file = st.file_uploader("Media File:", type=['png', 'jpg', 'mp4'])
                    with t_u: ns_url = st.text_input("Or Video Link:")

                    if st.button("➕ Create Step", type="primary"):
                        step_data = {"title": ns_title, "text": ns_text, "icon": "", "image": "", "video_url": ""}
                        
                        if ns_icon:
                            ipath = os.path.join(MEDIA_DIR, ns_icon.name)
                            with open(ipath, "wb") as f: f.write(ns_icon.getbuffer())
                            step_data["icon"] = ns_icon.name
                        
                        if ns_file:
                            fpath = os.path.join(MEDIA_DIR, ns_file.name)
                            with open(fpath, "wb") as f: f.write(ns_file.getbuffer())
                            step_data["image"] = ns_file.name
                        elif ns_url:
                            step_data["video_url"] = ns_url
                        
                        current_steps.append(step_data)
                        if cat_key not in data: data[cat_key] = {"description": "", "steps": []}
                        data[cat_key]["steps"] = current_steps
                        save_data(data)
                        st.success("Created!")
                        st.rerun()

            st.divider()
            
            # --- LIST EXISTING STEPS ---
            st.subheader(f"Edit Existing Steps ({len(current_steps)})")
            
            for i, step in enumerate(current_steps):
                # Smart Label
                parts = []
                if step.get("title"): parts.append(f"📌 {step['title']}")
                if step.get("image"): parts.append("🖼️ Media")
                if step.get("video_url"): parts.append("🎥 Video")
                label = f"Step {i+1}: " + " | ".join(parts) if parts else f"Step {i+1}"

                with st.expander(label, expanded=False):
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        new_title = st.text_input("Title:", value=step.get("title", ""), key=f"t_{cat_key}_{i}")
                        new_text = st.text_area("Text:", value=step.get("text", ""), key=f"txt_{cat_key}_{i}", height=120)
                    with c2:
                        new_url = st.text_input("Video URL:", value=step.get("video_url", ""), key=f"url_{cat_key}_{i}")
                        
                        # Show current media
                        curr_img = step.get("image")
                        if curr_img: st.caption(f"Current: {curr_img}")
                        
                        new_media = st.file_uploader("Replace Media:", key=f"up_{cat_key}_{i}")
                        if new_media:
                            fpath = os.path.join(MEDIA_DIR, new_media.name)
                            with open(fpath, "wb") as f: f.write(new_media.getbuffer())
                            # Update immediately
                            current_steps[i]["image"] = new_media.name
                            save_data(data)
                            st.rerun()

                    # Controls
                    col_save, col_up, col_down, col_del = st.columns([2, 1, 1, 1])
                    
                    # We save text updates on interaction (below) but allow buttons for order
                    if col_up.button("⬆️", key=f"sup_{cat_key}_{i}") and i > 0:
                        current_steps[i], current_steps[i-1] = current_steps[i-1], current_steps[i]
                        save_data(data)
                        st.rerun()
                    if col_down.button("⬇️", key=f"sdown_{cat_key}_{i}") and i < len(current_steps)-1:
                         current_steps[i], current_steps[i+1] = current_steps[i+1], current_steps[i]
                         save_data(data)
                         st.rerun()
                    if col_del.button("🗑️", key=f"sdel_{cat_key}_{i}", type="primary"):
                        current_steps.pop(i)
                        data[cat_key]["steps"] = current_steps
                        save_data(data)
                        st.rerun()

                    # Save text/title changes
                    if new_title != step.get("title", "") or new_text != step.get("text", "") or new_url != step.get("video_url", ""):
                         current_steps[i]["title"] = new_title
                         current_steps[i]["text"] = new_text
                         current_steps[i]["video_url"] = new_url
                         data[cat_key]["steps"] = current_steps
                         save_data(data)

    # --- TAB: CREATE CATEGORY ---
    with tab_create:
        st.header("New Category")
        nc_name = st.text_input("Category Name (include emoji):", placeholder="e.g. 🎒 New Guide")
        nc_id = st.text_input("ID (unique, lowercase):", placeholder="new_guide")
        
        if st.button("Create Category"):
            if nc_id in categories:
                st.error("ID already exists!")
            elif not nc_name or not nc_id:
                st.error("Fill all fields.")
            else:
                data["categories_list"][nc_id] = nc_name
                # Ensure it's preserved in data
                data[nc_id] = {"description": "", "steps": []}
                save_data(data)
                st.success("Created!")
                st.rerun()

    # --- TAB: HOME PAGE ---
    with tab_home:
        st.header("Home Page Editing")
        h_text = st.text_area("Welcome Text (Markdown):", value=data["home"].get("text", ""), height=200)
        
        st.write("Current Logo:")
        curr_logo = data["home"].get("logo")
        if curr_logo: st.image(os.path.join(MEDIA_DIR, curr_logo), width=100)
        
        new_logo = st.file_uploader("Update Logo:", type=['png', 'jpg'])
        if st.button("Save Home Settings"):
            data["home"]["text"] = h_text
            if new_logo:
                lpath = os.path.join(MEDIA_DIR, new_logo.name)
                with open(lpath, "wb") as f: f.write(new_logo.getbuffer())
                data["home"]["logo"] = new_logo.name
            
            save_data(data)
            st.success("Saved.")

    # --- TAB: USERS ---
    with tab_users:
        st.header("Admin Users")
        nu_user = st.text_input("New Username")
        nu_pass = st.text_input("New Password", type="password")
        if st.button("Add Admin"):
            if not nu_user or not nu_pass:
                st.error("Fill all fields.")
            else:
                if "admins" not in data: data["admins"] = {}
                data["admins"][nu_user] = hash_password(nu_pass)
                save_data(data)
                st.success("User added.")
                st.rerun()
        
        st.divider()
        st.write("Existing Admins:")
        for user in list(data.get("admins", {}).keys()):
            c1, c2 = st.columns([3, 1])
            c1.write(f"- {user}")
            if c2.button("Remove", key=f"rm_usr_{user}"):
                del data["admins"][user]
                save_data(data)
                st.rerun()

    # --- TAB: LOGS ---
    with tab_logs:
        st.header("System Logs")
        if st.button("Clear Logs"):
            data["system_logs"] = []
            save_data(data)
            st.rerun()
        st.code("\n".join(data.get("system_logs", [])))
