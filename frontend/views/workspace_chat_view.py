import streamlit as st
import uuid
from api_client import APIClient
from config import StateKeys, DEFAULT_MODEL_FAMILY, DEFAULT_MODEL_NAME
from components.alerts import show_error, show_info


def render_workspace_chat_view():
    st.header("💬 Authenticated Workspace Chat")
    st.caption("Perform RAG conversational search over uploaded workspace documents using customizable LLMs.")

    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)
    if not jwt_token:
        show_info("Please log in with Super Admin credentials in the **Authentication** tab first.")
        return

    active_ws = st.session_state.get(StateKeys.ACTIVE_WORKSPACE_ID, "")

    # Controls row
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        workspace_id = st.text_input("Workspace ID", value=active_ws, placeholder="Workspace UUID")
    with col2:
        model_family = st.selectbox("Model Family", ["gemini", "groq", "llama-3", "qwen"], index=0)
    with col3:
        if model_family == "gemini":
            model_name = st.selectbox("Model Name", ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"], index=0)
        else:
            model_name = st.selectbox("Model Name", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"], index=0)
    with col4:
        if st.button("🗑️ Reset Chat", use_container_width=True):
            st.session_state[StateKeys.CHAT_MESSAGES] = []
            st.session_state[StateKeys.ACTIVE_SESSION_ID] = str(uuid.uuid4())
            st.rerun()

    # Session ID initialization
    if StateKeys.ACTIVE_SESSION_ID not in st.session_state or not st.session_state[StateKeys.ACTIVE_SESSION_ID]:
        st.session_state[StateKeys.ACTIVE_SESSION_ID] = str(uuid.uuid4())

    st.caption(f"Session ID: `{st.session_state[StateKeys.ACTIVE_SESSION_ID]}`")

    # Messages initialization
    if StateKeys.CHAT_MESSAGES not in st.session_state:
        st.session_state[StateKeys.CHAT_MESSAGES] = []

    # Render chat history
    for msg in st.session_state[StateKeys.CHAT_MESSAGES]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("📚 Retrieved Knowledge Chunks"):
                    st.json(msg["sources"])

    # Chat Input
    if prompt := st.chat_input("Ask any question about documents in this workspace..."):
        if not workspace_id:
            show_error("Please enter a Workspace ID before chatting.")
            return

        # Add user message
        st.session_state[StateKeys.CHAT_MESSAGES].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call RAG API
        with st.chat_message("assistant"):
            with st.spinner("Retrieving relevant context and generating response..."):
                try:
                    resp = APIClient.ask_chat(
                        workspace_id=workspace_id,
                        question=prompt,
                        model_family=model_family,
                        model_name=model_name,
                        session_id=st.session_state[StateKeys.ACTIVE_SESSION_ID]
                    )

                    answer = resp.get("answer", str(resp))
                    sources = resp.get("sources", [])

                    st.markdown(answer)
                    if sources:
                        with st.expander("📚 Retrieved Knowledge Chunks"):
                            st.json(sources)

                    st.session_state[StateKeys.CHAT_MESSAGES].append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except Exception as e:
                    show_error(f"Chat error: {str(e)}")
