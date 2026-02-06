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

@st.cache_data(show_spinner=False, ttl=5)
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
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
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

def save_step_feedback(category_key, step_index, feedback_type):
    """Save feedback for a specific step. feedback_type: 'helpful' or 'not_helpful'"""
    try:
        data = load_data()
        
        if "step_feedback" not in data:
            data["step_feedback"] = {}
        
        step_key = f"{category_key}_step_{step_index}"
        
        if step_key not in data["step_feedback"]:
            data["step_feedback"][step_key] = {"helpful": 0, "not_helpful": 0}
        
        data["step_feedback"][step_key][feedback_type] += 1
        
        save_data(data)
    except Exception as e:
        print(f"Error saving step feedback: {e}")

def get_user_id():
    """Generate a simple user ID based on session. In production, use SSO."""
    if "user_id" not in st.session_state:
        # Use timestamp + random for unique ID (persists in session)
        import hashlib
        import random
        unique = f"{datetime.datetime.now().timestamp()}_{random.randint(1000, 9999)}"
        st.session_state.user_id = hashlib.md5(unique.encode()).hexdigest()[:8]
    return st.session_state.user_id

def save_user_progress(category_key, completed_steps):
    """Save user progress to JSON for persistence."""
    try:
        data = load_data()
        user_id = get_user_id()
        
        if "user_progress" not in data:
            data["user_progress"] = {}
        
        if user_id not in data["user_progress"]:
            data["user_progress"][user_id] = {}
        
        data["user_progress"][user_id][category_key] = completed_steps
        save_data(data)
    except Exception as e:
        print(f"Error saving user progress: {e}")

def load_user_progress(category_key):
    """Load user progress from JSON."""
    try:
        data = load_data()
        user_id = get_user_id()
        
        return data.get("user_progress", {}).get(user_id, {}).get(category_key, [])
    except Exception:
        return []

def save_bookmark(category_key, step_index, add=True):
    """Add or remove a bookmark for a step."""
    try:
        data = load_data()
        user_id = get_user_id()
        
        if "bookmarks" not in data:
            data["bookmarks"] = {}
        if user_id not in data["bookmarks"]:
            data["bookmarks"][user_id] = []
        
        bookmark_id = f"{category_key}_step_{step_index}"
        
        if add and bookmark_id not in data["bookmarks"][user_id]:
            data["bookmarks"][user_id].append(bookmark_id)
        elif not add and bookmark_id in data["bookmarks"][user_id]:
            data["bookmarks"][user_id].remove(bookmark_id)
        
        save_data(data)
    except Exception as e:
        print(f"Error saving bookmark: {e}")

def load_bookmarks():
    """Load user's bookmarks."""
    try:
        data = load_data()
        user_id = get_user_id()
        return data.get("bookmarks", {}).get(user_id, [])
    except Exception:
        return []

# ========================================
# ANALYTICS FUNCTIONS
# ========================================

def track_page_view(category_key):
    """Track a page view for analytics. Called when user visits a guide."""
    try:
        # Use a session flag to avoid counting refreshes
        view_key = f"viewed_{category_key}"
        if st.session_state.get(view_key):
            return  # Already counted this session
        
        data = load_data()
        
        if "analytics" not in data:
            data["analytics"] = {"page_views": {}, "completions": {}, "daily_views": {}}
        
        # Update page views count
        if category_key not in data["analytics"]["page_views"]:
            data["analytics"]["page_views"][category_key] = {"views": 0, "last_viewed": ""}
        
        data["analytics"]["page_views"][category_key]["views"] += 1
        data["analytics"]["page_views"][category_key]["last_viewed"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Track daily views for trends
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if "daily_views" not in data["analytics"]:
            data["analytics"]["daily_views"] = {}
        if today not in data["analytics"]["daily_views"]:
            data["analytics"]["daily_views"][today] = {}
        if category_key not in data["analytics"]["daily_views"][today]:
            data["analytics"]["daily_views"][today][category_key] = 0
        data["analytics"]["daily_views"][today][category_key] += 1
        
        save_data(data)
        st.session_state[view_key] = True  # Mark as viewed this session
        
    except Exception as e:
        print(f"Error tracking page view: {e}")

def track_completion(category_key):
    """Track when a user completes all steps in a guide."""
    try:
        # Use a session flag to avoid counting multiple completions
        complete_key = f"completed_{category_key}"
        if st.session_state.get(complete_key):
            return  # Already counted this session
        
        data = load_data()
        
        if "analytics" not in data:
            data["analytics"] = {"page_views": {}, "completions": {}, "daily_views": {}}
        
        if "completions" not in data["analytics"]:
            data["analytics"]["completions"] = {}
        
        if category_key not in data["analytics"]["completions"]:
            data["analytics"]["completions"][category_key] = 0
        
        data["analytics"]["completions"][category_key] += 1
        
        save_data(data)
        st.session_state[complete_key] = True
        
    except Exception as e:
        print(f"Error tracking completion: {e}")

def get_analytics_data():
    """Get all analytics data for the admin dashboard."""
    try:
        data = load_data()
        return data.get("analytics", {"page_views": {}, "completions": {}, "daily_views": {}})
    except Exception:
        return {"page_views": {}, "completions": {}, "daily_views": {}}

def get_analytics_summary():
    """Get summarized analytics for quick display."""
    analytics = get_analytics_data()
    categories = load_data().get("categories_list", {})
    
    summary = []
    for cat_key, cat_name in categories.items():
        views_data = analytics.get("page_views", {}).get(cat_key, {"views": 0, "last_viewed": "Never"})
        completions = analytics.get("completions", {}).get(cat_key, 0)
        
        total_steps = len(load_data().get(cat_key, {}).get("steps", []))
        completion_rate = round((completions / views_data["views"] * 100) if views_data["views"] > 0 else 0, 1)
        
        summary.append({
            "key": cat_key,
            "name": cat_name,
            "views": views_data["views"],
            "last_viewed": views_data.get("last_viewed", "Never"),
            "completions": completions,
            "completion_rate": completion_rate,
            "total_steps": total_steps
        })
    
    return sorted(summary, key=lambda x: x["views"], reverse=True)

# ========================================
# VERSION HISTORY FUNCTIONS
# ========================================

MAX_VERSIONS = 10  # Keep last 10 versions per category

def save_version_snapshot(category_key, author="admin"):
    """
    Save a snapshot of the current content before making changes.
    Call this BEFORE any content modification.
    """
    try:
        data = load_data()
        
        # Get current content
        current_content = data.get(category_key, {})
        if not current_content:
            return  # Nothing to snapshot
        
        # Initialize version history structure
        if "version_history" not in data:
            data["version_history"] = {}
        if category_key not in data["version_history"]:
            data["version_history"][category_key] = []
        
        history = data["version_history"][category_key]
        
        # Determine next version number
        version_num = len(history) + 1
        
        # Create snapshot
        import copy
        snapshot = {
            "version": version_num,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "author": author,
            "content_snapshot": copy.deepcopy(current_content),
            "step_count": len(current_content.get("steps", []))
        }
        
        # Add to history
        history.append(snapshot)
        
        # Trim to max versions (keep most recent)
        if len(history) > MAX_VERSIONS:
            data["version_history"][category_key] = history[-MAX_VERSIONS:]
        
        # Update last_updated timestamp on the category
        if category_key in data:
            data[category_key]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        save_data(data)
        
    except Exception as e:
        print(f"Error saving version snapshot: {e}")

def get_version_history(category_key):
    """Get the version history for a category."""
    try:
        data = load_data()
        history = data.get("version_history", {}).get(category_key, [])
        # Return in reverse order (newest first)
        return list(reversed(history))
    except Exception:
        return []

def restore_version(category_key, version_number):
    """Restore content to a previous version."""
    try:
        data = load_data()
        history = data.get("version_history", {}).get(category_key, [])
        
        # Find the version
        target_version = None
        for v in history:
            if v["version"] == version_number:
                target_version = v
                break
        
        if not target_version:
            return False
        
        # Save current state before restoring
        save_version_snapshot(category_key, author="restore")
        
        # Restore the content
        data[category_key] = target_version["content_snapshot"]
        data[category_key]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        save_data(data)
        log_event(f"Restored {category_key} to version {version_number}")
        return True
        
    except Exception as e:
        print(f"Error restoring version: {e}")
        return False

def get_last_updated(category_key):
    """Get the last updated timestamp for a category."""
    try:
        data = load_data()
        return data.get(category_key, {}).get("last_updated", None)
    except Exception:
        return None

# ========================================
# QUIZ SYSTEM FUNCTIONS
# ========================================

def get_quiz(category_key):
    """Get quiz questions for a category."""
    try:
        data = load_data()
        return data.get(category_key, {}).get("quiz", [])
    except Exception:
        return []

def save_quiz(category_key, quiz_questions):
    """Save quiz questions for a category."""
    try:
        data = load_data()
        if category_key in data:
            data[category_key]["quiz"] = quiz_questions
            save_data(data)
            return True
    except Exception as e:
        print(f"Error saving quiz: {e}")
    return False

def save_quiz_result(category_key, score, total, passed):
    """Save a user's quiz result."""
    try:
        data = load_data()
        user_id = get_user_id()
        
        if "quiz_results" not in data:
            data["quiz_results"] = {}
        if user_id not in data["quiz_results"]:
            data["quiz_results"][user_id] = {}
        
        data["quiz_results"][user_id][category_key] = {
            "score": score,
            "total": total,
            "passed": passed,
            "completed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_data(data)
    except Exception as e:
        print(f"Error saving quiz result: {e}")

def get_quiz_result(category_key):
    """Get user's quiz result for a category."""
    try:
        data = load_data()
        user_id = get_user_id()
        return data.get("quiz_results", {}).get(user_id, {}).get(category_key, None)
    except Exception:
        return None

# ========================================
# USER PROFILE & TRACKING FUNCTIONS
# ========================================

def get_user_profile():
    """Get the current user's profile."""
    try:
        data = load_data()
        user_id = get_user_id()
        return data.get("user_profiles", {}).get(user_id, None)
    except Exception:
        return None

def save_user_profile(name, email, department=""):
    """Save user profile information."""
    try:
        data = load_data()
        user_id = get_user_id()
        
        if "user_profiles" not in data:
            data["user_profiles"] = {}
        
        data["user_profiles"][user_id] = {
            "name": name,
            "email": email,
            "department": department,
            "registered_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "user_id": user_id
        }
        save_data(data)
        return True
    except Exception as e:
        print(f"Error saving user profile: {e}")
        return False

def get_all_users_progress():
    """Get progress data for all registered users (for admin)."""
    try:
        data = load_data()
        profiles = data.get("user_profiles", {})
        progress = data.get("user_progress", {})
        quiz_results = data.get("quiz_results", {})
        categories = data.get("categories_list", {})
        
        users_data = []
        for user_id, profile in profiles.items():
            user_progress = progress.get(user_id, {})
            user_quizzes = quiz_results.get(user_id, {})
            
            # Calculate completed guides
            completed_guides = 0
            for cat_key in categories.keys():
                cat_data = data.get(cat_key, {})
                total_steps = len(cat_data.get("steps", []))
                user_steps = len(user_progress.get(cat_key, []))
                if total_steps > 0 and user_steps >= total_steps:
                    completed_guides += 1
            
            # Calculate quiz pass rate
            passed_quizzes = sum(1 for q in user_quizzes.values() if q.get("passed", False))
            
            users_data.append({
                "user_id": user_id,
                "name": profile.get("name", "Unknown"),
                "email": profile.get("email", ""),
                "department": profile.get("department", ""),
                "registered_at": profile.get("registered_at", ""),
                "guides_completed": completed_guides,
                "total_guides": len(categories),
                "quizzes_passed": passed_quizzes,
                "completion_pct": round(completed_guides / len(categories) * 100) if categories else 0
            })
        
        return sorted(users_data, key=lambda x: x["completion_pct"], reverse=True)
    except Exception as e:
        print(f"Error getting all users progress: {e}")
        return []

def get_user_completion_status(user_id=None):
    """Get detailed completion status for a specific user."""
    try:
        data = load_data()
        if user_id is None:
            user_id = get_user_id()
            
        profile = data.get("user_profiles", {}).get(user_id, {})
        progress = data.get("user_progress", {}).get(user_id, {})
        quiz_results = data.get("quiz_results", {}).get(user_id, {})
        categories = data.get("categories_list", {})
        
        status = []
        for cat_key, cat_name in categories.items():
            cat_data = data.get(cat_key, {})
            total_steps = len(cat_data.get("steps", []))
            user_steps = len(progress.get(cat_key, []))
            quiz = quiz_results.get(cat_key, {})
            
            status.append({
                "key": cat_key,
                "name": cat_name,
                "steps_completed": user_steps,
                "total_steps": total_steps,
                "progress_pct": round(user_steps / total_steps * 100) if total_steps > 0 else 0,
                "guide_complete": user_steps >= total_steps if total_steps > 0 else False,
                "quiz_passed": quiz.get("passed", False),
                "quiz_score": quiz.get("score", 0),
                "quiz_total": quiz.get("total", 0)
            })
        
        return {
            "profile": profile,
            "categories": status,
            "all_complete": all(s["guide_complete"] for s in status)
        }
    except Exception as e:
        print(f"Error getting user completion status: {e}")
        return {"profile": {}, "categories": [], "all_complete": False}
