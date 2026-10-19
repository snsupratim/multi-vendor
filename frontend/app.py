import streamlit as st
from config import StateKeys, DEFAULT_API_BASE_URL
from components.navbar import render_navbar
from views.auth_view import render_auth_view
from views.vendors_view import render_vendors_view
from views.workspaces_view import render_workspaces_view
from views.documents_view import render_documents_view
from views.api_keys_view import render_api_keys_view
from views.workspace_chat_view import render_workspace_chat_view
from views.public_chat_view import render_public_chat_view
from views.modules_view import render_modules_view
from views.analytics_chat_view import render_analytics_chat_view
from views.history_view import render_history_view
from views.billing_view import render_billing_view
from views.models_view import render_models_view
from views.logs_view import render_logs_view

# Streamlit Page Config
st.set_page_config(
    page_title="Multi-Tenant RAG & Analytics Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Global Session State
if StateKeys.API_BASE_URL not in st.session_state:
    st.session_state[StateKeys.API_BASE_URL] = DEFAULT_API_BASE_URL
if StateKeys.JWT_TOKEN not in st.session_state:
    st.session_state[StateKeys.JWT_TOKEN] = None
if StateKeys.USER_INFO not in st.session_state:
    st.session_state[StateKeys.USER_INFO] = {}
if StateKeys.ACTIVE_VENDOR_ID not in st.session_state:
    st.session_state[StateKeys.ACTIVE_VENDOR_ID] = ""
if StateKeys.ACTIVE_WORKSPACE_ID not in st.session_state:
    st.session_state[StateKeys.ACTIVE_WORKSPACE_ID] = ""
if StateKeys.ACTIVE_MODULE_ID not in st.session_state:
    st.session_state[StateKeys.ACTIVE_MODULE_ID] = ""
if StateKeys.API_KEY not in st.session_state:
    st.session_state[StateKeys.API_KEY] = ""

# Sidebar Controls
with st.sidebar:
    st.title("🏢 Multi-Tenant Platform")
    st.caption("Enterprise RAG & SQL Analytics")
    st.markdown("---")

    # Backend Settings
    with st.expander("⚙️ Backend Server URL"):
        current_url = st.session_state.get(StateKeys.API_BASE_URL, DEFAULT_API_BASE_URL)
        new_url = st.text_input("API Base URL", value=current_url)
        if new_url != current_url:
            st.session_state[StateKeys.API_BASE_URL] = new_url
            st.rerun()

    # Navigation Menu
    NAV_OPTIONS = [
        "🔑 1. Authentication",
        "🏢 2. Vendors (Tenants)",
        "📁 3. Workspaces",
        "📄 4. Document Ingestion",
        "🔐 5. API Keys Provisioning",
        "💬 6. Workspace RAG Chat",
        "🌍 7. Public Chat Widget",
        "🧩 8. Global Modules & Access",
        "📊 9. Analytics (Text-to-SQL)",
        "🕰️ 10. Chat History",
        "💳 11. Billing & Token Tracking",
        "🧠 12. AI Model Registry",
        "📋 13. System Logs & Health"
    ]

    selected_page = st.radio("Navigation", NAV_OPTIONS, index=0)

    st.markdown("---")
    # Quick Context Status
    active_v = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "")
    active_w = st.session_state.get(StateKeys.ACTIVE_WORKSPACE_ID, "")
    active_m = st.session_state.get(StateKeys.ACTIVE_MODULE_ID, "")

    st.markdown("##### 📌 Active Context")
    if active_v:
        st.caption(f"**Vendor:** `{active_v[:14]}...`")
    if active_w:
        st.caption(f"**Workspace:** `{active_w[:14]}...`")
    if active_m:
        st.caption(f"**Module:** `{active_m[:14]}...`")

# Render Top Status Bar
render_navbar()

# Route Page Selection
if "1. Authentication" in selected_page:
    render_auth_view()
elif "2. Vendors" in selected_page:
    render_vendors_view()
elif "3. Workspaces" in selected_page:
    render_workspaces_view()
elif "4. Document" in selected_page:
    render_documents_view()
elif "5. API Keys" in selected_page:
    render_api_keys_view()
elif "6. Workspace RAG" in selected_page:
    render_workspace_chat_view()
elif "7. Public Chat" in selected_page:
    render_public_chat_view()
elif "8. Global Modules" in selected_page:
    render_modules_view()
elif "9. Analytics" in selected_page:
    render_analytics_chat_view()
elif "10. Chat History" in selected_page:
    render_history_view()
elif "11. Billing" in selected_page:
    render_billing_view()
elif "12. AI Model" in selected_page:
    render_models_view()
elif "13. System Logs" in selected_page:
    render_logs_view()
