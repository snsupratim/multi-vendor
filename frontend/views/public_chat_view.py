import streamlit as st
import uuid
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_info


def render_public_chat_view():
    st.header("🌍 Public Chat API & Widget Simulator")
    st.caption("Simulate customer-facing embeddable web chat widgets powered by `X-API-Key` with active token quota & rate-limiting.")

    current_api_key = st.session_state.get(StateKeys.API_KEY, "")

    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        api_key_input = st.text_input("Public API Key (X-API-Key)", value=current_api_key, type="password", placeholder="vndr_sk_...")
    with col2:
        chat_mode = st.selectbox("API Endpoint", ["/v1/public/chat (Workspace RAG)", "/v1/public/module-chat (Global Module)"])
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state["public_chat_msgs"] = []
            st.rerun()

    if "public_chat_msgs" not in st.session_state:
        st.session_state["public_chat_msgs"] = []

    if "public_session_id" not in st.session_state:
        st.session_state["public_session_id"] = str(uuid.uuid4())

    st.caption(f"Public Session ID: `{st.session_state['public_session_id']}`")

    # Display chat history
    for msg in st.session_state["public_chat_msgs"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Send a public message..."):
        if not api_key_input:
            show_error("API Key is required to test public endpoints.")
            return

        st.session_state["public_chat_msgs"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Processing public request through rate limiter & RAG..."):
                try:
                    if "public/chat" in chat_mode:
                        resp = APIClient.ask_public_chat(
                            api_key=api_key_input,
                            question=prompt,
                            session_id=st.session_state["public_session_id"]
                        )
                        answer = resp.get("answer", str(resp))
                    else:
                        active_vendor = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "")
                        active_module = st.session_state.get(StateKeys.ACTIVE_MODULE_ID, "")
                        resp = APIClient.public_module_chat(
                            api_key=api_key_input,
                            vendor_id=active_vendor,
                            module_id=active_module,
                            question=prompt,
                            session_id=st.session_state["public_session_id"]
                        )
                        answer = resp.get("answer", str(resp))

                    st.markdown(answer)
                    st.session_state["public_chat_msgs"].append({"role": "assistant", "content": answer})

                except Exception as e:
                    show_error(f"Public API error: {str(e)}")
