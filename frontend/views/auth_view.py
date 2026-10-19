import streamlit as st
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_success, show_info


def render_auth_view():
    st.header("🔑 Authentication & User Management")
    st.caption("Manage authentication, register super admins/tenant users, and inspect JWT session tokens.")

    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)

    tab_login, tab_register, tab_session = st.tabs(["🔐 Login", "📝 Register New User", "📋 Active Session & Profile"])

    with tab_login:
        st.subheader("Login to Platform")
        with st.form("login_form"):
            email = st.text_input("Email", value="admin@platform.com", placeholder="user@domain.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("🚀 Login", use_container_width=True)

            if submit:
                if not email or not password:
                    show_error("Please enter both email and password.")
                else:
                    try:
                        with st.spinner("Authenticating..."):
                            data = APIClient.login(email=email, password=password)
                            token = data.get("access_token")
                            user_data = data.get("user", {})

                            st.session_state[StateKeys.JWT_TOKEN] = token
                            st.session_state[StateKeys.USER_INFO] = user_data
                            show_success(f"Logged in successfully as {user_data.get('name', email)}!")
                            st.rerun()
                    except Exception as e:
                        show_error(f"Login failed: {str(e)}")

    with tab_register:
        st.subheader("Register New Account")
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="e.g. John Doe")
            reg_email = st.text_input("Email Address", placeholder="e.g. admin@company.com")
            reg_password = st.text_input("Password", type="password", placeholder="Enter strong password")
            submit_reg = st.form_submit_button("✨ Register Account", use_container_width=True)

            if submit_reg:
                if not name or not reg_email or not reg_password:
                    show_error("All fields are required.")
                else:
                    try:
                        with st.spinner("Creating account..."):
                            resp = APIClient.register(name=name, email=reg_email, password=reg_password)
                            show_success(f"User {resp.get('email', reg_email)} registered successfully! Please proceed to Login.")
                    except Exception as e:
                        show_error(f"Registration failed: {str(e)}")

    with tab_session:
        st.subheader("Current Session & Profile")
        if not jwt_token:
            show_info("No active JWT session. Please log in first.")
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("#### Logged In Profile")
                try:
                    profile = APIClient.get_me()
                    st.json(profile)
                except Exception as e:
                    show_error(f"Failed to fetch profile: {str(e)}")

                with st.expander("Show Raw JWT Bearer Token"):
                    st.code(jwt_token, language="text")

            with col2:
                if st.button("🚪 Logout", use_container_width=True, type="primary"):
                    st.session_state[StateKeys.JWT_TOKEN] = None
                    st.session_state[StateKeys.USER_INFO] = {}
                    show_success("Logged out successfully.")
                    st.rerun()
