import json
import os
import datetime
import streamlit as st

DATA_FILE = "content_data.json"
DEFAULT_CATEGORIES = {
    "mfa": "🔐 1. MFA (Microsoft 2FA)",
    "vpn": "🛡️ 2. VPN Config",
    "outlook": "📧 3. Outlook & Email",
    "mobile": "📱 4. Mobile APN",
    "software_center": "💿 5. Software Center",
    "other": "📚 6. Other Tutorials"
}

@st.cache_data(show_spinner=False)
def load_data():
    base_structure = {
        "home": {"logo": "", "text": "# Welcome!\nSelect a guide from the left."},
        "categories_list": DEFAULT_CATEGORIES,
        "system_logs": [],
        "admins": {},
        "faq": [
            {"q": "I cannot login to Outlook.", "a": "Please ensure you have reset your initial password on a Prysmian device first."},
            {"q": "VPN says 'Gateway Unreachable'.", "a": "Check your internet connection and try switching from WiFi to Mobile Hotspot to test."}
        ],
        "feedback_stats": {"helpful": 0, "not_helpful": 0}
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
    if "faq" not in data:
        data["faq"] = base_structure["faq"]
        data_modified = True
    if "feedback_stats" not in data:
        data["feedback_stats"] = base_structure["feedback_stats"]
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
        # Clear cache to ensure next load gets fresh data
        st.cache_data.clear()
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
