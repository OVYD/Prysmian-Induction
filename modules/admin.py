import streamlit as st
import os
from modules.data_manager import (
    load_data, save_data, log_event, get_analytics_summary, get_analytics_data, 
    save_version_snapshot, get_version_history, restore_version, get_last_updated,
    get_quiz, save_quiz, get_all_users_progress, get_user_completion_status
)
from modules.auth import hash_password
from modules.pdf_export import get_pdf_download_link

MEDIA_DIR = "images"

def render_admin_panel():
    st.title("⚙️ Admin Dashboard")
    
    tab_cats, tab_reorder, tab_create, tab_home, tab_faq, tab_analytics, tab_feedback, tab_users, tab_logs = st.tabs([
        "📂 Manage Content", 
        "⇄ Reorder Menu",
        "➕ Create Category", 
        "🏠 Home Page",
        "❓ FAQ Manager",
        "📈 Analytics",
        "📊 Feedback",
        "👥 Manage Users", 
        "📋 Logs"
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
                save_version_snapshot(cat_key)  # Save version before change
                if cat_key not in data: data[cat_key] = {"description": "", "steps": []}
                data[cat_key]["description"] = new_desc
                save_data(data)
            
            # --- VERSION HISTORY EXPANDER ---
            version_history = get_version_history(cat_key)
            last_updated = get_last_updated(cat_key)
            
            with st.expander(f"📜 Version History ({len(version_history)} versions)", expanded=False):
                if last_updated:
                    st.caption(f"**Last Updated:** {last_updated}")
                
                if not version_history:
                    st.info("No version history yet. Changes will be tracked automatically.")
                else:
                    for ver in version_history[:5]:  # Show last 5
                        v_col1, v_col2, v_col3 = st.columns([2, 2, 1])
                        with v_col1:
                            st.markdown(f"**v{ver['version']}** - {ver['step_count']} steps")
                        with v_col2:
                            st.caption(ver['timestamp'])
                        with v_col3:
                            if st.button("↩️", key=f"restore_{cat_key}_{ver['version']}", help="Restore this version"):
                                if restore_version(cat_key, ver['version']):
                                    st.success(f"Restored to v{ver['version']}!")
                                    st.rerun()
                                else:
                                    st.error("Failed to restore.")
            
            # --- QUIZ EDITOR ---
            st.markdown("---")
            st.subheader("🧠 Quiz Questions")
            st.caption("Add quiz questions to test users after completing this guide.")
            
            quiz_questions = get_quiz(cat_key)
            
            # Add new question
            with st.container(border=True):
                st.markdown("**➕ Add New Question**")
                new_q = st.text_input("Question:", key=f"new_quiz_q_{cat_key}")
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    new_a1 = st.text_input("Answer 1:", key=f"new_quiz_a1_{cat_key}")
                    new_a2 = st.text_input("Answer 2:", key=f"new_quiz_a2_{cat_key}")
                with col_a2:
                    new_a3 = st.text_input("Answer 3:", key=f"new_quiz_a3_{cat_key}")
                    new_a4 = st.text_input("Answer 4:", key=f"new_quiz_a4_{cat_key}")
                correct_idx = st.radio("Correct Answer:", ["1", "2", "3", "4"], horizontal=True, key=f"new_quiz_correct_{cat_key}")
                
                if st.button("➕ Add Question", key=f"add_quiz_{cat_key}"):
                    if new_q and new_a1 and new_a2:
                        answers = [a for a in [new_a1, new_a2, new_a3, new_a4] if a]
                        quiz_questions.append({
                            "q": new_q,
                            "answers": answers,
                            "correct": int(correct_idx) - 1
                        })
                        save_quiz(cat_key, quiz_questions)
                        st.success("Question added!")
                        st.rerun()
                    else:
                        st.error("Fill in question and at least 2 answers.")
            
            # Existing questions
            if quiz_questions:
                st.markdown(f"**📝 Existing Questions ({len(quiz_questions)})**")
                for qi, qq in enumerate(quiz_questions):
                    with st.expander(f"Q{qi+1}: {qq.get('q', 'Question')[:40]}..."):
                        st.write(f"**{qq.get('q')}**")
                        for ai, ans in enumerate(qq.get("answers", [])):
                            prefix = "✅ " if ai == qq.get("correct", 0) else ""
                            st.write(f"{prefix}{ai+1}. {ans}")
                        if st.button("🗑️ Delete", key=f"del_quiz_{cat_key}_{qi}"):
                            quiz_questions.pop(qi)
                            save_quiz(cat_key, quiz_questions)
                            st.rerun()
            else:
                st.info("No quiz questions yet. Add some above!")

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
                        save_version_snapshot(cat_key)  # Save version before delete
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

    # --- TAB: FAQ MANAGER ---
    with tab_faq:
        st.header("❓ FAQ Manager")
        st.caption("Add, edit, or remove frequently asked questions.")
        
        faqs = data.get("faq", [])
        
        # Add new FAQ
        st.subheader("➕ Add New FAQ")
        with st.container(border=True):
            new_q = st.text_input("Question:", placeholder="How do I reset my password?")
            new_a = st.text_area("Answer:", placeholder="To reset your password, go to...", height=100)
            
            if st.button("Add FAQ", type="primary"):
                if new_q and new_a:
                    faqs.append({"q": new_q, "a": new_a})
                    data["faq"] = faqs
                    save_data(data)
                    st.success("FAQ added!")
                    st.rerun()
                else:
                    st.error("Please fill in both question and answer.")
        
        st.divider()
        
        # Existing FAQs
        st.subheader(f"📝 Existing FAQs ({len(faqs)})")
        
        for i, faq in enumerate(faqs):
            with st.expander(f"Q: {faq.get('q', 'No question')[:50]}...", expanded=False):
                edit_q = st.text_input("Question:", value=faq.get("q", ""), key=f"faq_q_{i}")
                edit_a = st.text_area("Answer:", value=faq.get("a", ""), key=f"faq_a_{i}", height=100)
                
                col_save, col_up, col_down, col_del = st.columns([2, 1, 1, 1])
                
                # Save changes
                if edit_q != faq.get("q") or edit_a != faq.get("a"):
                    faqs[i]["q"] = edit_q
                    faqs[i]["a"] = edit_a
                    data["faq"] = faqs
                    save_data(data)
                
                # Move up
                if col_up.button("⬆️", key=f"faq_up_{i}") and i > 0:
                    faqs[i], faqs[i-1] = faqs[i-1], faqs[i]
                    data["faq"] = faqs
                    save_data(data)
                    st.rerun()
                
                # Move down
                if col_down.button("⬇️", key=f"faq_down_{i}") and i < len(faqs)-1:
                    faqs[i], faqs[i+1] = faqs[i+1], faqs[i]
                    data["faq"] = faqs
                    save_data(data)
                    st.rerun()
                
                # Delete
                if col_del.button("🗑️", key=f"faq_del_{i}", type="primary"):
                    faqs.pop(i)
                    data["faq"] = faqs
                    save_data(data)
                    st.rerun()

    # --- TAB: ANALYTICS DASHBOARD ---
    with tab_analytics:
        st.header("📈 Usage Analytics")
        st.caption("Track guide views, completions, and user engagement.")
        
        analytics = get_analytics_data()
        summary = get_analytics_summary()
        
        if not analytics.get("page_views"):
            st.info("No analytics data yet. Data will appear as users visit guides.")
        else:
            # Summary Metrics
            total_views = sum(item["views"] for item in summary)
            total_completions = sum(item["completions"] for item in summary)
            avg_completion_rate = round(sum(item["completion_rate"] for item in summary) / len(summary), 1) if summary else 0
            
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("👁️ Total Views", total_views)
            with m2:
                st.metric("✅ Completions", total_completions)
            with m3:
                st.metric("📊 Avg Completion Rate", f"{avg_completion_rate}%")
            with m4:
                st.metric("📚 Active Guides", len([s for s in summary if s["views"] > 0]))
            
            st.divider()
            
            # Top Viewed Guides Chart
            st.subheader("🏆 Top Viewed Guides")
            
            if summary:
                # Create a simple bar chart using columns
                for item in summary[:5]:  # Top 5
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        # Progress bar visualization
                        max_views = max(s["views"] for s in summary) if summary else 1
                        pct = int((item["views"] / max_views) * 100) if max_views > 0 else 0
                        st.markdown(f"""
                        <div style="background: #2D3748; border-radius: 4px; padding: 8px; margin: 4px 0;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                <span>{item["name"][:30]}</span>
                                <span style="color: #00D2BE;">{item["views"]} views</span>
                            </div>
                            <div style="background: #1a1a2e; height: 8px; border-radius: 4px;">
                                <div style="background: linear-gradient(90deg, #00D2BE, #00B140); width: {pct}%; height: 100%; border-radius: 4px;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.caption(f"Completions: {item['completions']}")
                    with col3:
                        rate_color = "#00B140" if item["completion_rate"] >= 50 else "#FFA500" if item["completion_rate"] >= 25 else "#FF4444"
                        st.markdown(f"<span style='color: {rate_color};'>{item['completion_rate']}%</span>", unsafe_allow_html=True)
            
            st.divider()
            
            # Daily Trends (Last 7 Days)
            st.subheader("📅 Last 7 Days Activity")
            daily_views = analytics.get("daily_views", {})
            
            if daily_views:
                import datetime
                today = datetime.datetime.now()
                last_7_days = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
                
                for day in last_7_days:
                    day_data = daily_views.get(day, {})
                    total_day_views = sum(day_data.values())
                    day_label = datetime.datetime.strptime(day, "%Y-%m-%d").strftime("%a %d/%m")
                    
                    st.markdown(f"**{day_label}**: {total_day_views} views")
            else:
                st.caption("No daily data available yet.")
            
            st.divider()
            
            # Export PDF Button
            col_export, col_reset = st.columns([1, 1])
            with col_export:
                if st.button("📄 Export Report to PDF", type="primary"):
                    pdf_path = get_pdf_download_link()
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=f,
                                file_name="analytics_report.pdf",
                                mime="application/pdf"
                            )
                    else:
                        st.error("Failed to generate PDF.")
            
            with col_reset:
                # Clear Analytics Button
                if st.button("🗑️ Reset All Analytics", type="secondary"):
                    data["analytics"] = {"page_views": {}, "completions": {}, "daily_views": {}}
                    save_data(data)
                    st.success("Analytics data cleared!")
                    st.rerun()

    # --- TAB: FEEDBACK STATS ---
    with tab_feedback:
        st.header("📊 Feedback Analytics")
        st.caption("View user feedback statistics for each guide step.")
        
        step_feedback = data.get("step_feedback", {})
        
        if not step_feedback:
            st.info("No feedback has been collected yet. Feedback will appear here as users rate steps.")
        else:
            # Calculate totals
            total_helpful = sum(f.get("helpful", 0) for f in step_feedback.values())
            total_not_helpful = sum(f.get("not_helpful", 0) for f in step_feedback.values())
            total_votes = total_helpful + total_not_helpful
            
            # Summary metrics
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total Votes", total_votes)
            with m2:
                st.metric("👍 Helpful", total_helpful)
            with m3:
                st.metric("👎 Not Helpful", total_not_helpful)
            with m4:
                satisfaction_rate = round((total_helpful / total_votes * 100) if total_votes > 0 else 0, 1)
                st.metric("Satisfaction Rate", f"{satisfaction_rate}%")
            
            st.divider()
            
            # Filter by category
            filter_cat = st.selectbox(
                "Filter by Category:",
                ["All Categories"] + list(categories.values()),
                key="feedback_filter"
            )
            
            st.subheader("📋 Detailed Feedback by Step")
            
            # Process and display feedback
            for step_key, fb_data in sorted(step_feedback.items(), key=lambda x: x[1].get("not_helpful", 0), reverse=True):
                # Parse step key: "category_step_index"
                parts = step_key.split("_step_")
                if len(parts) != 2:
                    continue
                    
                cat_key, step_idx = parts[0], parts[1]
                cat_name = categories.get(cat_key, cat_key)
                
                # Apply filter
                if filter_cat != "All Categories" and cat_name != filter_cat:
                    continue
                
                helpful = fb_data.get("helpful", 0)
                not_helpful = fb_data.get("not_helpful", 0)
                total = helpful + not_helpful
                
                if total == 0:
                    continue
                
                # Get step title if available
                try:
                    step_data = data.get(cat_key, {}).get("steps", [])
                    step_title = step_data[int(step_idx)].get("title", f"Step {int(step_idx) + 1}")
                except:
                    step_title = f"Step {int(step_idx) + 1}"
                
                # Display with color coding
                ratio = helpful / total if total > 0 else 0
                color = "#00B140" if ratio >= 0.7 else "#FFA500" if ratio >= 0.4 else "#FF4444"
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.markdown(f"**{cat_name}** → {step_title}")
                    with c2:
                        st.markdown(f"👍 {helpful} &nbsp; 👎 {not_helpful}")
                    with c3:
                        st.markdown(f"<span style='color: {color}; font-weight: bold;'>{round(ratio * 100)}%</span>", unsafe_allow_html=True)
            
            st.divider()
            
            # Clear feedback option
            if st.button("🗑️ Clear All Feedback Data", type="secondary"):
                data["step_feedback"] = {}
                save_data(data)
                st.success("Feedback data cleared!")
                st.rerun()

    # --- TAB: USERS (User Progress Dashboard) ---
    with tab_users:
        st.header("👥 User Progress Tracking")
        st.caption("Monitor employee onboarding progress across all guides.")
        
        users_data = get_all_users_progress()
        
        if not users_data:
            st.info("No registered users yet. Users will appear here once they provide their name/email.")
        else:
            # Summary metrics
            m1, m2, m3, m4 = st.columns(4)
            total_users = len(users_data)
            completed_users = sum(1 for u in users_data if u["completion_pct"] == 100)
            avg_progress = round(sum(u["completion_pct"] for u in users_data) / total_users) if total_users else 0
            
            with m1:
                st.metric("👤 Total Users", total_users)
            with m2:
                st.metric("✅ Fully Completed", completed_users)
            with m3:
                st.metric("📊 Avg Progress", f"{avg_progress}%")
            with m4:
                st.metric("🧠 Quizzes Passed", sum(u["quizzes_passed"] for u in users_data))
            
            st.divider()
            
            # Search/Filter
            search_user = st.text_input("🔍 Search by name or email:")
            
            # User table
            st.subheader("📋 User Details")
            
            for user in users_data:
                # Apply search filter
                if search_user and search_user.lower() not in user["name"].lower() and search_user.lower() not in user["email"].lower():
                    continue
                
                # Color based on progress
                if user["completion_pct"] == 100:
                    status_icon = "🏆"
                    status_color = "#00B140"
                elif user["completion_pct"] >= 50:
                    status_icon = "📈"
                    status_color = "#FFA500"
                else:
                    status_icon = "🚀"
                    status_color = "#FF4444"
                
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                    with c1:
                        st.markdown(f"**{status_icon} {user['name']}**")
                        st.caption(user["email"])
                    with c2:
                        st.caption(f"Dept: {user['department'] or 'N/A'}")
                        st.caption(f"Joined: {user['registered_at']}")
                    with c3:
                        st.markdown(f"""
                        <div style='text-align: center;'>
                            <div style='font-size: 24px; color: {status_color};'>{user['completion_pct']}%</div>
                            <div style='font-size: 11px; color: #888;'>Progress</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c4:
                        st.markdown(f"""
                        <div style='text-align: center;'>
                            <div style='font-size: 24px;'>{user['guides_completed']}/{user['total_guides']}</div>
                            <div style='font-size: 11px; color: #888;'>Guides</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Expandable details
                    with st.expander("View Details"):
                        user_status = get_user_completion_status(user["user_id"])
                        for cat in user_status.get("categories", []):
                            prog_bar_color = "#00B140" if cat["guide_complete"] else "#00D2BE"
                            quiz_status = "✅ Passed" if cat["quiz_passed"] else (f"❌ {cat['quiz_score']}/{cat['quiz_total']}" if cat["quiz_total"] > 0 else "⏳ Not taken")
                            
                            col_name, col_prog, col_quiz = st.columns([3, 2, 1])
                            with col_name:
                                st.write(cat["name"][:30])
                            with col_prog:
                                st.progress(cat["progress_pct"] / 100)
                            with col_quiz:
                                st.caption(quiz_status)
        
        st.divider()
        
        # Admin Users Section
        st.subheader("🔐 Admin Users")
        nu_user = st.text_input("New Admin Username")
        nu_pass = st.text_input("New Admin Password", type="password")
        if st.button("Add Admin"):
            if not nu_user or not nu_pass:
                st.error("Fill all fields.")
            else:
                if "admins" not in data: data["admins"] = {}
                data["admins"][nu_user] = hash_password(nu_pass)
                save_data(data)
                st.success("Admin added.")
                st.rerun()
        
        st.caption("Existing Admins:")
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
