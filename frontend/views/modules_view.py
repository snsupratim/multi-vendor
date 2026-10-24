import streamlit as st
import pandas as pd
import json
from api_client import APIClient
from config import StateKeys
from components.alerts import show_error, show_success, show_info


def render_modules_view():
    st.header("🧩 Global Modules & Tenant Access")
    st.caption("Manage shared business modules (e.g. PAYROLL, LEAVE_MANAGEMENT), grant tenant permissions, and ingest SQL DDL schemas & business rules.")

    jwt_token = st.session_state.get(StateKeys.JWT_TOKEN)
    if not jwt_token:
        show_info("Please log in with Super Admin credentials in the **Authentication** tab first.")
        return

    active_vendor = st.session_state.get(StateKeys.ACTIVE_VENDOR_ID, "")
    active_module = st.session_state.get(StateKeys.ACTIVE_MODULE_ID, "")

    tab_list, tab_create, tab_grant, tab_rules, tab_schema = st.tabs([
        "📋 Modules Directory", 
        "➕ Create Global Module", 
        "🛡️ Grant Vendor Access", 
        "📥 Ingest Business Rules (JSON)", 
        "🗄️ Ingest SQL Schema DDL"
    ])

    with tab_list:
        st.subheader("Global Platform Modules")
        try:
            modules = APIClient.get_all_modules()
            if not modules:
                st.info("No global modules found.")
            else:
                df = pd.DataFrame(modules)
                st.dataframe(df, use_container_width=True)

                st.markdown("#### Select Active Module")
                mod_options = {f"{m.get('name', 'Module')} ({m.get('module_id', '')})": m.get('module_id', '') for m in modules}
                selected_mod = st.selectbox("Choose active module context:", list(mod_options.keys()))
                
                if st.button("Set as Active Module Context", type="primary"):
                    st.session_state[StateKeys.ACTIVE_MODULE_ID] = mod_options[selected_mod]
                    show_success(f"Active module set to: {mod_options[selected_mod]}")
                    st.rerun()

        except Exception as e:
            show_error(f"Failed to fetch modules: {str(e)}")

    with tab_create:
        st.subheader("Create New Global Module")
        with st.form("create_module_form"):
            name = st.text_input("Module Name (UPPERCASE)", placeholder="e.g. PAYROLL")
            desc = st.text_area("Description", placeholder="e.g. Global Payroll & Employee Text-to-SQL Analytics Engine")
            system_prompt = st.text_area(
                "Module System Prompt",
                value=(
                    "You are an enterprise Analytics and Text-to-SQL Agent. "
                    "Generate PostgreSQL queries and analytical components based on user questions. "
                    "Dynamically infer all filtering identifiers (e.g. company_id, vendor_id, branch_id, org_id, employee_id) "
                    "and relationships directly from the uploaded table schemas, DDL definitions, knowledge base rules, or user query context. "
                    "Never assume or hardcode a specific ID column unless it exists in the schema or is specified in the query."
                ),
                height=140
            )
            submit_mod = st.form_submit_button("🧩 Create Module", use_container_width=True)

            if submit_mod:
                if not name:
                    show_error("Module Name is required.")
                else:
                    try:
                        with st.spinner("Creating module..."):
                            resp = APIClient.create_module(name=name, description=desc, system_prompt=system_prompt)
                            m_id = resp.get("module_id", "")
                            st.session_state[StateKeys.ACTIVE_MODULE_ID] = m_id
                            show_success(f"Module '{name}' created successfully! ID: `{m_id}`")
                    except Exception as e:
                        show_error(f"Failed to create module: {str(e)}")

    with tab_grant:
        st.subheader("Grant Vendor Access to Module")
        with st.form("grant_access_form"):
            col1, col2 = st.columns(2)
            with col1:
                grant_module_id = st.text_input("Module ID", value=active_module, placeholder="Module UUID")
            with col2:
                grant_vendor_id = st.text_input("Vendor ID", value=active_vendor, placeholder="Vendor UUID")

            submit_grant = st.form_submit_button("🛡️ Grant Access Permission", use_container_width=True)

            if submit_grant:
                if not grant_module_id or not grant_vendor_id:
                    show_error("Both Module ID and Vendor ID are required.")
                else:
                    try:
                        with st.spinner("Granting access..."):
                            resp = APIClient.grant_vendor_module_access(module_id=grant_module_id, vendor_id=grant_vendor_id)
                            show_success(f"Access granted successfully to Vendor `{grant_vendor_id}` for Module `{grant_module_id}`!")
                    except Exception as e:
                        show_error(f"Grant access failed: {str(e)}")

    with tab_rules:
        st.subheader("Ingest Module Business Rules & Policies")
        with st.form("module_rules_form"):
            target_mod_rules = st.text_input("Module ID", value=active_module, key="mod_rules_id")
            page_content = st.text_area("Business Logic / Calculation Rules", height=150, placeholder="e.g. Overtime is 1.5x regular hourly pay after 40 hours per week...")
            meta_json = st.text_area("Metadata", value='{"topic": "overtime_calculation"}', height=70)
            submit_rule = st.form_submit_button("📥 Ingest Rule into Knowledge Base", use_container_width=True)

            if submit_rule:
                if not target_mod_rules or not page_content:
                    show_error("Module ID and Content are required.")
                else:
                    try:
                        parsed_meta = json.loads(meta_json) if meta_json else {}
                    except Exception as err:
                        show_error(f"Invalid JSON metadata: {err}")
                        return

                    try:
                        with st.spinner("Ingesting module knowledge..."):
                            resp = APIClient.upload_module_json(module_id=target_mod_rules, page_content=page_content, metadata=parsed_meta)
                            show_success("Module rule ingested successfully!")
                            st.json(resp)
                    except Exception as e:
                        show_error(f"Rule ingestion failed: {str(e)}")

    with tab_schema:
        st.subheader("Ingest Module SQL Schema DDL")
        with st.form("module_schema_form"):
            target_mod_schema = st.text_input("Module ID", value=active_module, key="mod_schema_id")
            table_name = st.text_input("Table Name", placeholder="e.g. employees")
            schema_ddl = st.text_area("SQL Schema DDL", height=120, placeholder="CREATE TABLE employees (id UUID PRIMARY KEY, vendor_id VARCHAR, name VARCHAR, department VARCHAR, salary NUMERIC);")
            desc = st.text_input("Table Description", placeholder="e.g. Employee master records partitioned by vendor_id")
            relationships = st.text_input("Relationships / Foreign Keys", placeholder="e.g. Linked to payroll_runs table via employee_id")

            submit_schema = st.form_submit_button("🗄️ Ingest SQL Schema", use_container_width=True)

            if submit_schema:
                if not target_mod_schema or not table_name or not schema_ddl:
                    show_error("Module ID, Table Name, and Schema DDL are required.")
                else:
                    try:
                        with st.spinner("Vectorizing SQL Schema DDL..."):
                            resp = APIClient.upload_module_schema(
                                module_id=target_mod_schema,
                                table_name=table_name,
                                schema_ddl=schema_ddl,
                                description=desc,
                                relationships=relationships
                            )
                            show_success("SQL Schema DDL ingested successfully!")
                            st.json(resp)
                    except Exception as e:
                        show_error(f"Schema ingestion failed: {str(e)}")
