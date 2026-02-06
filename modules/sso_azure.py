"""
Azure AD SSO Module for Prysmian Induction Portal
================================================

This module provides Azure Active Directory Single Sign-On integration.
Users are automatically authenticated using their company Microsoft accounts.

SETUP REQUIRED:
1. Configure Azure AD App Registration (see docs/AZURE_SSO_INTEGRATION.md)
2. Add credentials to .streamlit/secrets.toml
3. Install: pip install msal

USAGE:
    from modules.sso_azure import require_authentication, get_current_user
    
    # In main app:
    require_authentication()  # Will redirect to login if not authenticated
    user = get_current_user()
    print(user["email"])
"""

import streamlit as st

# Try to import MSAL, provide helpful error if not installed
try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False


def check_msal_installed():
    """Check if MSAL is available."""
    if not MSAL_AVAILABLE:
        st.error("⚠️ MSAL library not installed. Run: `pip install msal`")
        st.stop()


def get_azure_config():
    """Get Azure AD configuration from Streamlit secrets."""
    try:
        return {
            "client_id": st.secrets["azure"]["client_id"],
            "client_secret": st.secrets["azure"]["client_secret"],
            "tenant_id": st.secrets["azure"]["tenant_id"],
            "redirect_uri": st.secrets["azure"]["redirect_uri"]
        }
    except KeyError as e:
        return None


def get_msal_app():
    """Create MSAL confidential client application."""
    check_msal_installed()
    config = get_azure_config()
    if not config:
        return None
    
    return msal.ConfidentialClientApplication(
        client_id=config["client_id"],
        client_credential=config["client_secret"],
        authority=f"https://login.microsoftonline.com/{config['tenant_id']}"
    )


def get_auth_url():
    """Generate Azure AD login URL."""
    app = get_msal_app()
    if not app:
        return None
    
    config = get_azure_config()
    return app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=config["redirect_uri"]
    )


def handle_auth_callback(auth_code):
    """
    Exchange authorization code for tokens and extract user info.
    
    Returns:
        dict: User info with name, email, oid (Azure Object ID)
        None: If authentication failed
    """
    app = get_msal_app()
    if not app:
        return None
    
    config = get_azure_config()
    result = app.acquire_token_by_authorization_code(
        code=auth_code,
        scopes=["User.Read"],
        redirect_uri=config["redirect_uri"]
    )
    
    if "access_token" in result:
        # Extract user info from ID token claims
        claims = result.get("id_token_claims", {})
        return {
            "name": claims.get("name", ""),
            "email": claims.get("preferred_username", ""),
            "oid": claims.get("oid", ""),  # Azure Object ID - use as user_id
            "authenticated": True
        }
    
    # Log error for debugging
    if "error" in result:
        print(f"SSO Error: {result.get('error_description', result['error'])}")
    
    return None


def get_current_user():
    """Get current authenticated user from session."""
    return st.session_state.get("sso_user", None)


def is_authenticated():
    """Check if user is authenticated via SSO."""
    return st.session_state.get("sso_authenticated", False)


def logout():
    """Clear SSO session and redirect to Azure logout."""
    st.session_state.pop("sso_user", None)
    st.session_state.pop("sso_authenticated", None)
    
    # Azure logout URL (optional - fully signs out of Microsoft)
    config = get_azure_config()
    if config:
        tenant_id = config["tenant_id"]
        logout_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/logout"
        return logout_url
    return None


def require_authentication():
    """
    Require user to be authenticated. Shows login button if not.
    Call this at the start of your main app.
    
    Usage:
        require_authentication()
        # Code after this only runs if user is authenticated
    """
    # Check for auth callback (returning from Azure login)
    auth_code = st.query_params.get("code")
    if auth_code and not is_authenticated():
        user = handle_auth_callback(auth_code)
        if user:
            st.session_state.sso_user = user
            st.session_state.sso_authenticated = True
            
            # Auto-save user profile
            from modules.data_manager import save_user_profile
            save_user_profile(
                name=user["name"],
                email=user["email"],
                department=""  # Can be fetched from Azure AD groups
            )
            
            # Clear the auth code from URL
            st.query_params.clear()
            st.rerun()
    
    # Check if authenticated
    if not is_authenticated():
        # Check if Azure is configured
        config = get_azure_config()
        
        if not config:
            # Azure not configured - show warning but allow access (dev mode)
            st.sidebar.warning("⚠️ SSO not configured")
            return
        
        # Show login page
        st.title("🔐 Prysmian Induction Portal")
        st.markdown("### Please login with your company account")
        st.markdown("---")
        
        auth_url = get_auth_url()
        if auth_url:
            st.link_button(
                "🔵 Login with Microsoft", 
                auth_url, 
                type="primary",
                use_container_width=True
            )
        else:
            st.error("Failed to generate login URL. Check Azure configuration.")
        
        st.stop()  # Stop execution until authenticated


# ============================================================
# HELPER FUNCTION FOR data_manager.py
# ============================================================

def get_sso_user_id():
    """
    Get user ID from SSO session.
    Use this in data_manager.get_user_id() for SSO integration.
    
    Returns:
        str: Azure Object ID if authenticated, None otherwise
    """
    user = get_current_user()
    if user and user.get("oid"):
        return user["oid"]
    return None
