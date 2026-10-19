import streamlit as st
import pandas as pd
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_success, show_info


def render_workspaces_view():
    st.header("📁 Workspace Management")
    st.caption("Create and configure tenant workspaces, manage system prompts, and link workspaces to knowledge bases.")

    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)
    if not jwt_token:
        show_info("Please log in with Super Admin credentials in the **Authentication** tab first.")
        return

    active_vendor = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "")

    tab_list, tab_create, tab_prompt = st.tabs(["📋 Workspaces", "➕ Create Workspace", "⚙️ Update System Prompt"])

    with tab_list:
        st.subheader("Workspaces by Vendor")
        vendor_id_filter = st.text_input("Vendor ID to Filter:", value=active_vendor, placeholder="Enter vendor UUID")

        if st.button("🔄 Fetch Workspaces", use_container_width=True):
            if not vendor_id_filter:
                show_error("Please specify a Vendor ID to list workspaces.")
            else:
                try:
                    with st.spinner("Fetching workspaces..."):
                        workspaces = APIClient.get_vendor_workspaces(vendor_id_filter)
                        if not workspaces:
                            st.info(f"No workspaces found for Vendor `{vendor_id_filter}`.")
                        else:
                            df = pd.DataFrame(workspaces)
                            st.dataframe(df, use_container_width=True)

                            st.markdown("#### Select Active Workspace")
                            ws_options = {f"{ws.get('name', 'Workspace')} ({ws.get('workspace_id', ws.get('id', ''))})": ws.get('workspace_id', ws.get('id', '')) for ws in workspaces}
                            selected_ws = st.selectbox("Choose active workspace:", list(ws_options.keys()))
                            
                            if st.button("Set as Active Workspace Context", type="primary"):
                                st.session_state[StateKeys.ACTIVE_WORKSPACE_ID] = ws_options[selected_ws]
                                show_success(f"Active workspace set to: {ws_options[selected_ws]}")
                                st.rerun()
                except Exception as e:
                    show_error(f"Failed to fetch workspaces: {str(e)}")

    with tab_create:
        st.subheader("Create New Workspace")
        with st.form("create_ws_form"):
            vendor_for_ws = st.text_input("Vendor ID", value=active_vendor, placeholder="Vendor UUID")
            ws_name = st.text_input("Workspace Name", placeholder="e.g. HR Knowledge Base")
            ws_desc = st.text_area("Description", placeholder="e.g. Policies, manuals, benefits knowledge store")
            ws_prompt = st.text_area(
                "System Prompt",
                value="You are an expert HR assistant. Answer questions accurately and strictly based on provided context.",
                height=120
            )
            submit_ws = st.form_submit_button("📁 Create Workspace", use_container_width=True)

            if submit_ws:
                if not vendor_for_ws or not ws_name:
                    show_error("Vendor ID and Workspace Name are required.")
                else:
                    try:
                        with st.spinner("Creating workspace..."):
                            resp = APIClient.create_workspace(
                                vendor_id=vendor_for_ws,
                                name=ws_name,
                                description=ws_desc,
                                system_prompt=ws_prompt
                            )
                            ws_id = resp.get("workspace_id") or resp.get("id") or str(resp)
                            st.session_state[StateKeys.ACTIVE_WORKSPACE_ID] = ws_id
                            show_success(f"Workspace '{ws_name}' created successfully! Workspace ID: `{ws_id}`")
                    except Exception as e:
                        show_error(f"Failed to create workspace: {str(e)}")

    with tab_prompt:
        st.subheader("Update Workspace System Prompt")
        active_ws = st.session_state.get(StateKeys.ACTIVE_WORKSPACE_ID, "")
        ws_id_target = st.text_input("Target Workspace ID", value=active_ws)
        new_prompt = st.text_area("New System Prompt", height=150, placeholder="Enter new behavior/instructions...")

        if st.button("💾 Save System Prompt", type="primary", use_container_width=True):
            if not ws_id_target or not new_prompt:
                show_error("Workspace ID and System Prompt cannot be empty.")
            else:
                try:
                    with st.spinner("Updating system prompt..."):
                        resp = APIClient.update_workspace_prompt(workspace_id=ws_id_target, system_prompt=new_prompt)
                        show_success("Workspace system prompt updated successfully!")
                        st.json(resp)
                except Exception as e:
                    show_error(f"Failed to update prompt: {str(e)}")
