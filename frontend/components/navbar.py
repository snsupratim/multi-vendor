import streamlit as st
from config import StateKeys
from api_client import APIClient

def render_navbar():
    """
    Renders the top status bar displaying the active user, role, backend URL,
    and active tenant context (Vendor/Workspace).
    """
    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)
    user_info = st.session_state.get(StateKeys.USER_INFO, {})
    active_vendor = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "None")
    active_ws = st.session_state.get(StateKeys.ACTIVE_WORKSPACE_ID, "None")
    base_url = APIClient.get_base_url()

    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    
    with col1:
        st.markdown(f"🌐 **Backend:** `{base_url}`")
    
    with col2:
        if jwt_token:
            role = user_info.get("role", "USER")
            email = user_info.get("sub") or user_info.get("email", "Authenticated")
            st.markdown(f"👤 **User:** `{email}` (`{role}`)")
        else:
            st.markdown("⚠️ **Auth:** `Not Logged In`")
            
    with col3:
        st.markdown(f"🏢 **Vendor:** `{active_vendor[:10]}...`" if len(active_vendor) > 10 else f"🏢 **Vendor:** `{active_vendor}`")

    with col4:
        st.markdown(f"📁 **Workspace:** `{active_ws[:10]}...`" if len(active_ws) > 10 else f"📁 **Workspace:** `{active_ws}`")

    st.divider()
