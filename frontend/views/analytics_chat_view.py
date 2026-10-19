import streamlit as st
import uuid
from api_client import APIClient
from config import StateKeys
from components.visualizer import render_analytics_components, render_suggestions
from components.alerts import show_error, show_success, show_info


def render_analytics_chat_view():
    st.header("📊 Module Analytics & Text-to-SQL Chat")
    st.caption("Talk directly to your Postgres database using the LangGraph Text-to-SQL agent with dynamic interactive charts, metrics, and data tables.")

    active_vendor = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "")
    active_module = st.session_state.get(StateKeys.ACTIVE_MODULE_ID, "")

    # Top Control Bar
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
    with col1:
        vendor_id = st.text_input("Tenant Vendor ID", value=active_vendor, placeholder="Vendor UUID")
    with col2:
        module_id = st.text_input("Module ID", value=active_module, placeholder="Module UUID")
    with col3:
        model_family = st.selectbox("LLM Family", ["gemini", "groq", "llama-3"], index=0, key="analytics_fam")
    with col4:
        if model_family == "gemini":
            model_name = st.selectbox("LLM Model", ["gemini-2.5-flash", "gemini-1.5-pro"], index=0, key="analytics_mod")
        else:
            model_name = st.selectbox("LLM Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"], index=0, key="analytics_mod")
    with col5:
        if st.button("🗑️ Reset", use_container_width=True):
            st.session_state[StateKeys.ANALYTICS_MESSAGES] = []
            st.session_state["analytics_session_id"] = str(uuid.uuid4())
            st.rerun()

    # DB Connection Quick Tester
    with st.expander("🛠️ Test Live Postgres Connection"):
        if st.button("Ping Payroll / Analytics Database"):
            try:
                db_res = APIClient.test_analytics_db()
                if db_res.get("status") == "success":
                    show_success(f"Connected! Database Version: {db_res.get('version')} (URL: {db_res.get('url_used')})")
                else:
                    show_error(f"DB Error: {db_res.get('message')}")
            except Exception as e:
                show_error(f"Failed to test DB: {str(e)}")

    # Initialize Session
    if "analytics_session_id" not in st.session_state or not st.session_state["analytics_session_id"]:
        st.session_state["analytics_session_id"] = str(uuid.uuid4())

    st.caption(f"Active Analytics Session: `{st.session_state['analytics_session_id']}`")

    if StateKeys.ANALYTICS_MESSAGES not in st.session_state:
        st.session_state[StateKeys.ANALYTICS_MESSAGES] = []

    # Display History
    for msg in st.session_state[StateKeys.ANALYTICS_MESSAGES]:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                render_analytics_components(msg.get("components", []))
                if "suggestions" in msg and msg["suggestions"]:
                    render_suggestions(msg["suggestions"])

    # Handle quick suggestion click trigger
    def handle_query_submission(query_text: str):
        if not vendor_id or not module_id:
            show_error("Both Vendor ID and Module ID are required to run Analytics queries.")
            return

        st.session_state[StateKeys.ANALYTICS_MESSAGES].append({"role": "user", "content": query_text})
        
        with st.chat_message("user"):
            st.markdown(query_text)

        with st.chat_message("assistant"):
            with st.spinner("🤖 SQL Agent thinking, executing SQL queries, and generating visualization..."):
                try:
                    data = APIClient.analytics_chat(
                        vendor_id=vendor_id,
                        module_id=module_id,
                        question=query_text,
                        model_family=model_family,
                        model_name=model_name,
                        session_id=st.session_state["analytics_session_id"]
                    )

                    # Update session ID if backend returns one
                    if data.get("session_id"):
                        st.session_state["analytics_session_id"] = data["session_id"]

                    components = data.get("components", [])
                    suggestions = data.get("suggestions", [])

                    render_analytics_components(components)
                    if suggestions:
                        render_suggestions(suggestions)

                    st.session_state[StateKeys.ANALYTICS_MESSAGES].append({
                        "role": "assistant",
                        "components": components,
                        "suggestions": suggestions
                    })

                except Exception as e:
                    show_error(f"Analytics Agent execution failed: {str(e)}")

    # Chat Input Box
    if prompt := st.chat_input("Ask any database or analytics question (e.g. 'Show salary distribution by department in a pie chart')..."):
        handle_query_submission(prompt)
