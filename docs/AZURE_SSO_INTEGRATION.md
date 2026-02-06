# Azure AD SSO Integration Guide

## 📋 Overview

This guide explains how to integrate Azure Active Directory (AAD) Single Sign-On
with the Prysmian Induction Portal for automatic user authentication.

---

## 🔧 Prerequisites

1. **Azure AD Tenant** with admin access
2. **App Registration** in Azure Portal
3. Python packages: `msal` or `streamlit-msal`

```bash
pip install msal streamlit-msal
```

---

## 📝 Step 1: Azure Portal Configuration

### 1.1 Register Application

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory
2. App registrations → New registration
3. Configure:
   - **Name**: `Prysmian Induction Portal`
   - **Redirect URI**: `http://localhost:8501` (dev) or production URL
   - **Supported account types**: Single tenant

### 1.2 Configure Authentication

1. Go to Authentication → Add platform → Web
2. Add redirect URIs:
   - `http://localhost:8501/` (development)
   - `https://your-production-url.com/` (production)
3. Enable **ID tokens** under Implicit grant

### 1.3 Get Credentials

From **Overview**, copy:
- **Application (client) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Directory (tenant) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

From **Certificates & secrets** → New client secret:
- **Client Secret**: `xxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 📝 Step 2: Streamlit Secrets Configuration

Create `.streamlit/secrets.toml`:

```toml
[azure]
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
tenant_id = "YOUR_TENANT_ID"
redirect_uri = "http://localhost:8501"
```

---

## 📝 Step 3: Code Integration

### 3.1 Create `modules/sso_azure.py`

```python
"""
Azure AD SSO Module for Prysmian Induction Portal
"""
import streamlit as st
import msal

def get_msal_app():
    """Create MSAL confidential client application."""
    return msal.ConfidentialClientApplication(
        client_id=st.secrets["azure"]["client_id"],
        client_credential=st.secrets["azure"]["client_secret"],
        authority=f"https://login.microsoftonline.com/{st.secrets['azure']['tenant_id']}"
    )

def get_auth_url():
    """Generate Azure AD login URL."""
    app = get_msal_app()
    return app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=st.secrets["azure"]["redirect_uri"]
    )

def handle_auth_callback(auth_code):
    """Exchange authorization code for tokens and user info."""
    app = get_msal_app()
    result = app.acquire_token_by_authorization_code(
        code=auth_code,
        scopes=["User.Read"],
        redirect_uri=st.secrets["azure"]["redirect_uri"]
    )
    
    if "access_token" in result:
        # Get user info from token claims
        id_token_claims = result.get("id_token_claims", {})
        return {
            "name": id_token_claims.get("name", ""),
            "email": id_token_claims.get("preferred_username", ""),
            "oid": id_token_claims.get("oid", ""),  # Azure Object ID
            "authenticated": True
        }
    return None

def get_current_user():
    """Get current authenticated user from session."""
    return st.session_state.get("sso_user", None)

def is_authenticated():
    """Check if user is authenticated via SSO."""
    return st.session_state.get("sso_authenticated", False)

def logout():
    """Clear SSO session."""
    st.session_state.pop("sso_user", None)
    st.session_state.pop("sso_authenticated", None)
```

### 3.2 Modify `induction.py` (Entry Point)

```python
import streamlit as st
from modules.sso_azure import get_auth_url, handle_auth_callback, is_authenticated, get_current_user
from modules.data_manager import save_user_profile

# Check for auth callback
auth_code = st.query_params.get("code")
if auth_code and not is_authenticated():
    user = handle_auth_callback(auth_code)
    if user:
        st.session_state.sso_user = user
        st.session_state.sso_authenticated = True
        # Auto-save profile from SSO
        save_user_profile(
            name=user["name"],
            email=user["email"],
            department=""  # Can be fetched from Azure groups
        )
        # Clear the code from URL
        st.query_params.clear()
        st.rerun()

# Require authentication
if not is_authenticated():
    st.title("🔐 Login Required")
    st.markdown("Please login with your Prysmian account to continue.")
    auth_url = get_auth_url()
    st.link_button("🔵 Login with Microsoft", auth_url, type="primary")
    st.stop()

# User is authenticated - continue with normal app
# ... rest of your app code
```

### 3.3 Modify `data_manager.py` - get_user_id()

Replace the random ID generation with SSO-based ID:

```python
def get_user_id():
    """Get user ID from SSO or session."""
    # First check for SSO user
    sso_user = st.session_state.get("sso_user")
    if sso_user and sso_user.get("oid"):
        return sso_user["oid"]  # Use Azure Object ID
    
    # Fallback to session-based ID (for testing)
    if "user_id" not in st.session_state:
        import hashlib
        import random
        unique = f"{datetime.datetime.now().timestamp()}_{random.randint(1000, 9999)}"
        st.session_state.user_id = hashlib.md5(unique.encode()).hexdigest()[:8]
    return st.session_state.user_id
```

---

## 📝 Step 4: Display User Info

In `ui_components.py`, the sidebar already shows the user profile:

```python
user_profile = get_user_profile()
if user_profile:
    st.sidebar.success(f"✅ {user_profile.get('name', user_profile.get('email', 'User'))}")
```

---

## 🔒 Security Considerations

1. **Never commit `secrets.toml`** - Add to `.gitignore`
2. **Use HTTPS in production** - Required for secure OAuth
3. **Token expiration** - Implement token refresh logic
4. **Logout endpoint** - Add Azure logout URL redirect

---

## 🧪 Testing

1. Run locally with dev redirect URI
2. Login with test Azure account
3. Verify profile auto-creation in `content_data.json`
4. Check progress tracking works with SSO user ID

---

## 📚 References

- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [Azure AD App Registration](https://docs.microsoft.com/azure/active-directory/develop/quickstart-register-app)
- [Streamlit Authentication](https://docs.streamlit.io/library/advanced-features/authentication)

---

*Created by Dinulescu Cosmin Ovidiu (Gemini/Claude)*
