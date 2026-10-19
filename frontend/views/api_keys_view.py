import streamlit as st
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_success, show_info


def render_api_keys_view():
    st.header("🔑 API Key Provisioning")
    st.caption("Generate secure API keys for tenant workspaces to power embeddable widgets and public customer-facing APIs.")

    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)
    if not jwt_token:
        show_info("Please log in with Super Admin credentials in the **Authentication** tab first.")
        return

    active_ws = st.session_state.get(StateKeys.ACTIVE_WORKSPACE_ID, "")
    current_key = st.session_state.get(StateKeys.API_KEY, "")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Generate New Workspace API Key")
        with st.form("create_api_key_form"):
            ws_id = st.text_input("Workspace ID", value=active_ws, placeholder="Workspace UUID")
            key_name = st.text_input("Key Label / Description", placeholder="e.g. Production Web Chatbot Key")
            submit = st.form_submit_button("⚡ Generate Secret API Key", use_container_width=True)

            if submit:
                if not ws_id or not key_name:
                    show_error("Workspace ID and Key Label are required.")
                else:
                    try:
                        with st.spinner("Generating API key..."):
                            resp = APIClient.create_api_key(workspace_id=ws_id, name=key_name)
                            secret_key = resp.get("api_key", "")
                            key_id = resp.get("api_key_id", "")

                            st.session_state[StateKeys.API_KEY] = secret_key
                            show_success("API Key generated successfully!")
                            st.warning("⚠️ **Copy this secret key now.** You won't be able to see it again.")
                            st.code(secret_key, language="text")
                            st.caption(f"API Key ID: `{key_id}`")
                    except Exception as e:
                        show_error(f"Failed to generate API Key: {str(e)}")

    with col2:
        st.subheader("Active Session API Key")
        st.caption("This key is stored in your current UI session for testing public endpoints.")
        manual_key = st.text_input("Manual API Key Input", value=current_key, placeholder="vndr_sk_...", type="password")
        if st.button("Set Active Session Key"):
            st.session_state[StateKeys.API_KEY] = manual_key
            show_success("Session API Key updated!")

        if current_key:
            st.markdown(f"**Current Key Status:** `Active ({current_key[:12]}...)`")
        else:
            st.markdown("**Current Key Status:** `None set`")
