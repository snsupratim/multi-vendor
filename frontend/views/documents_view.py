import streamlit as st
import json
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_success, show_info


def render_documents_view():
    st.header("📄 Document Ingestion & Knowledge Base")
    st.caption("Upload documents (PDF, DOCX, TXT) or raw JSON knowledge snippets to vectorize and store in the RAG knowledge base.")

    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)
    if not jwt_token:
        show_info("Please log in with Super Admin credentials in the **Authentication** tab first.")
        return

    active_vendor = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "")
    active_ws = st.session_state.get(StateKeys.ACTIVE_WORKSPACE_ID, "")

    tab_file, tab_json = st.tabs(["📤 File Upload (PDF/DOCX/TXT)", "📝 Raw JSON / Text Ingestion"])

    with tab_file:
        st.subheader("Upload Document File")
        with st.form("file_upload_form"):
            col1, col2 = st.columns(2)
            with col1:
                target_vendor = st.text_input("Vendor ID", value=active_vendor, placeholder="Vendor UUID")
            with col2:
                target_ws = st.text_input("Workspace ID", value=active_ws, placeholder="Workspace UUID")

            uploaded_file = st.file_uploader("Choose a file (PDF, TXT, DOCX)", type=["pdf", "txt", "docx", "md"])
            submit_upload = st.form_submit_button("⚡ Ingest & Vectorize File", use_container_width=True)

            if submit_upload:
                if not target_vendor or not target_ws:
                    show_error("Both Vendor ID and Workspace ID are required.")
                elif not uploaded_file:
                    show_error("Please select a file to upload.")
                else:
                    try:
                        with st.spinner(f"Ingesting '{uploaded_file.name}' into vector database..."):
                            file_bytes = uploaded_file.read()
                            resp = APIClient.upload_document_file(
                                workspace_id=target_ws,
                                vendor_id=target_vendor,
                                file_name=uploaded_file.name,
                                file_bytes=file_bytes
                            )
                            show_success(f"File '{uploaded_file.name}' ingested successfully!")
                            st.json(resp)
                    except Exception as e:
                        show_error(f"File ingestion failed: {str(e)}")

    with tab_json:
        st.subheader("Ingest Structured JSON / Policy Text")
        with st.form("json_upload_form"):
            col1, col2 = st.columns(2)
            with col1:
                json_vendor = st.text_input("Vendor ID", value=active_vendor, key="json_vendor_id")
            with col2:
                json_ws = st.text_input("Workspace ID", value=active_ws, key="json_ws_id")

            page_content = st.text_area(
                "Document Content (Text / Markdown / Policy Rules)",
                height=180,
                placeholder="e.g. Standard probation period is 3 months with performance review on day 80..."
            )
            metadata_str = st.text_area(
                "Metadata (JSON Format)",
                value='{"category": "HR_POLICY", "department": "All"}',
                height=80
            )

            submit_json = st.form_submit_button("📥 Ingest JSON Knowledge", use_container_width=True)

            if submit_json:
                if not json_vendor or not json_ws or not page_content:
                    show_error("Vendor ID, Workspace ID, and Document Content are required.")
                else:
                    try:
                        parsed_meta = json.loads(metadata_str) if metadata_str else {}
                    except Exception as err:
                        show_error(f"Invalid JSON in Metadata: {err}")
                        return

                    try:
                        with st.spinner("Embedding and ingesting text chunks..."):
                            resp = APIClient.upload_json_document(
                                workspace_id=json_ws,
                                vendor_id=json_vendor,
                                page_content=page_content,
                                metadata=parsed_meta
                            )
                            show_success("Knowledge chunk ingested successfully!")
                            st.json(resp)
                    except Exception as e:
                        show_error(f"Ingestion failed: {str(e)}")
