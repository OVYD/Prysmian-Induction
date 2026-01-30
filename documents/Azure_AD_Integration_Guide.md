# Technical Guide: Azure Active Directory (Entra ID) Integration

To connect the **Prysmian Induction App** with the company's Active Directory (AD), we will use **Microsoft Entra ID (formerly Azure AD)** via the `OIDC` (OpenID Connect) protocol. This ensures employees can log in with their existing company email/password.

---

## 📅 Phase 1: Azure Setup (Requires IT Admin)

You need to ask the Central IT Team to register this application in the **Azure Portal**.
**Request to IT:**
> "Please register a new Enterprise Application (Service Principal) for the Induction Portal."

**They need to provide you with:**
1.  **Client ID** (App ID)
2.  **Client Secret** (Password)
3.  **Tenant ID** (Directory ID)

**Configuration Settings:**
*   **Redirect URI**: `https://prysmian-induction.streamlit.app/oauth2callback`
*   **Permissions (Scopes)**: `User.Read` (to get their name and email).

---

## 🛠️ Phase 2: Code Implementation

We will use the library `msal` (Microsoft Authentication Library) for Python.

### 1. New Dependencies
Add to `requirements.txt`:
```text
msal==1.28.0
requests==2.31.0
```

### 2. Authentication Logic (`modules/ad_auth.py`)
*This is a conceptual snippet of how the code will look.*

```python
import msal
import streamlit as st

CLIENT_ID = st.secrets["azure"]["client_id"]
CLIENT_SECRET = st.secrets["azure"]["client_secret"]
AUTHORITY = f"https://login.microsoftonline.com/{st.secrets['azure']['tenant_id']}"
REDIRECT_PATH = "/oauth2callback"

def get_auth_url():
    """Generates the Microsoft Login Link"""
    app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
    auth_url = app.get_authorization_request_url(scopes=["User.Read"], redirect_uri=st.secrets["azure"]["redirect_uri"])
    return auth_url

def get_token_from_code(code):
    """Exchanges the temporary code for a User Token"""
    app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
    result = app.acquire_token_by_authorization_code(code, scopes=["User.Read"], redirect_uri=st.secrets["azure"]["redirect_uri"])
    return result
```

### 3. Protecting the App (`app.py`)
We modify `app.py` to check for login before showing content.

```python
if "user" not in st.session_state:
    st.info("🔒 Please login with your Prysmian account to continue.")
    url = get_auth_url()
    st.markdown(f'<a href="{url}" target="_self" class="btn-primary">Sign In with Microsoft</a>', unsafe_allow_html=True)
    st.stop() # Prevents loading the rest of the app
else:
    # Show App Content
    render_sidebar()
    render_home_page()
```

---

## 🔐 Phase 3: Deployment Secrets
On Streamlit Cloud, specific secrets must be added securely:

```toml
[azure]
client_id = "xxxx-xxxx-xxxx"
client_secret = "xxxx-xxxx-xxxx"
tenant_id = "xxxx-xxxx-xxxx"
redirect_uri = "https://prysmian-induction.streamlit.app"
```

## ✅ Benefits
1.  **Single Sign-On (SSO)**: No new passwords to remember.
2.  **Auto-Onboarding**: We can automatically detect the user's Department from AD and show relevant guides (e.g., show "Developer Tools" only to IT staff).
3.  **Security**: If an employee leaves Prysmian, their access is automatically revoked.
