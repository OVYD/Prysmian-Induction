# Prysmian Induction Portal - Project Overview

## 📋 Project Summary

A Streamlit-based employee induction/onboarding portal for Prysmian.
Features interactive guides, quizzes, progress tracking, and completion certificates.

---

## 🏗️ Architecture

```
induction.py          # Main entry point
├── modules/
│   ├── ui_components.py    # UI rendering (sidebar, pages, guides)
│   ├── data_manager.py     # Data persistence & business logic
│   ├── admin.py            # Admin dashboard
│   ├── auth.py             # Authentication (for Azure SSO)
│   ├── pdf_export.py       # PDF report generation
│   ├── certificate.py      # Certificate generation
│   └── search.py           # Search functionality
├── assets/style.css        # Custom CSS styling
└── content_data.json       # Content database
```

---

## 📦 Modules & Functions

### `data_manager.py` - Core Data Layer

| Function | Description |
|----------|-------------|
| `load_data()` | Load content from JSON |
| `save_data(data)` | Persist data to JSON |
| `get_user_id()` | Get/generate user session ID |
| `save_user_profile(name, email, dept)` | **SSO Integration Point** |
| `get_user_profile()` | Get current user profile |
| `save_user_progress(cat, steps)` | Track completed steps |
| `load_user_progress(cat)` | Load user's progress |
| `track_page_view(cat)` | Analytics: page views |
| `track_completion(cat)` | Analytics: completions |
| `get_analytics_summary()` | Dashboard metrics |
| `get_quiz(cat)` | Get quiz questions |
| `save_quiz_result(cat, score, total, passed)` | Store quiz result |
| `get_all_users_progress()` | Admin: all users data |
| `get_user_completion_status(user_id)` | Detailed user progress |

### `auth.py` - Authentication

| Function | Description |
|----------|-------------|
| `hash_password(pw)` | SHA-256 password hash |
| `verify_password(hash, pw)` | Verify password |
| `login_sidebar()` | Admin login UI |

### `pdf_export.py` - Reports

| Function | Description |
|----------|-------------|
| `generate_analytics_pdf()` | Create analytics PDF report |
| `get_pdf_download_link()` | Generate & return PDF path |

### `certificate.py` - Certificates

| Function | Description |
|----------|-------------|
| `generate_certificate(name, email)` | Create PDF certificate |
| `can_get_certificate()` | Check eligibility |

---

## 🔑 Key Integration Points

### For Azure SSO Integration

1. **User Profile Saving**: `data_manager.save_user_profile(name, email, dept)`
2. **Session ID**: `data_manager.get_user_id()` - Replace with SSO token ID
3. **Auth Module**: `auth.py` - Add SSO provider logic

### For External Systems

- **Progress Data**: `get_all_users_progress()` returns list of all user progress
- **Analytics**: `get_analytics_summary()` for dashboard integration
- **Completion Events**: `track_completion()` can trigger webhooks

---

## 📊 Data Structure

```json
{
  "mfa": { "title": "...", "steps": [...], "quiz": [...] },
  "user_progress": { "user_id": { "category": [0,1,2] } },
  "user_profiles": { "user_id": { "name", "email", "dept" } },
  "quiz_results": { "user_id": { "cat": { "score", "passed" } } },
  "analytics": { "page_views": {}, "completions": {} }
}
```

---

## 🚀 Deployment Requirements

- Python 3.9+
- Streamlit 1.30+
- fpdf2 (PDF generation)

```bash
pip install streamlit fpdf2
streamlit run induction.py
```

---

*Created by Dinulescu Cosmin Ovidiu (Gemini/Claude)*
