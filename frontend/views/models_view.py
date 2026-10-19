import streamlit as st
import pandas as pd
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_success, show_info


def render_models_view():
    st.header("🧠 AI Model Registry")
    st.caption("Manage supported LLM models across Gemini, Groq, Ollama, OpenAI, and Anthropic.")

    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)

    tab_list, tab_create = st.tabs(["📋 Registered Models", "➕ Register New Model"])

    with tab_list:
        st.subheader("Available AI Models")
        try:
            models = APIClient.list_models()
            if not models:
                st.info("No AI models registered in registry yet.")
            else:
                df = pd.DataFrame(models)
                st.dataframe(df, use_container_width=True)

                if jwt_token:
                    st.markdown("#### Delete Model (Super Admin)")
                    del_model_id = st.text_input("Model ID to Delete", placeholder="Enter model ID")
                    if st.button("🗑️ Delete Model", type="primary"):
                        if del_model_id:
                            try:
                                APIClient.delete_model(del_model_id)
                                show_success(f"Model `{del_model_id}` deleted successfully.")
                                st.rerun()
                            except Exception as e:
                                show_error(f"Failed to delete model: {str(e)}")
        except Exception as e:
            show_error(f"Failed to list models: {str(e)}")

    with tab_create:
        st.subheader("Register New AI Model")
        if not jwt_token:
            show_info("Please log in with Super Admin credentials in the **Authentication** tab to register models.")
        else:
            with st.form("create_model_form"):
                family = st.text_input("Model Family", placeholder="e.g. gemini, groq, llama-3, qwen")
                name = st.text_input("Model Identifier / API Name", placeholder="e.g. gemini-2.5-flash, llama-3.3-70b-versatile")
                provider = st.text_input("Provider", placeholder="e.g. gemini, groq, vertex")
                display_name = st.text_input("Display Name", placeholder="e.g. Google Gemini 2.5 Flash")

                submit_model = st.form_submit_button("🧠 Register Model", use_container_width=True)

                if submit_model:
                    if not family or not name or not provider or not display_name:
                        show_error("All fields are required.")
                    else:
                        try:
                            with st.spinner("Registering model..."):
                                resp = APIClient.create_model(
                                    model_family=family,
                                    model_name=name,
                                    provider=provider,
                                    display_name=display_name
                                )
                                show_success(f"Model '{display_name}' registered successfully!")
                                st.json(resp)
                        except Exception as e:
                            show_error(f"Failed to register model: {str(e)}")
