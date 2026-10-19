import requests
from typing import Dict, Any, Optional, List
import streamlit as st
from config import StateKeys, DEFAULT_API_BASE_URL


class APIClient:
    """
    Centralized HTTP client for all Multi-Tenant Platform endpoints.
    Handles JWT tokens, X-API-Key headers, query parameters, file uploads, and unified error parsing.
    """

    @staticmethod
    def get_base_url() -> str:
        return st.session_state.get(StateKeys.API_BASE_URL, DEFAULT_API_BASE_URL).rstrip("/")

    @staticmethod
    def _headers(use_jwt: bool = True, custom_api_key: Optional[str] = None) -> Dict[str, str]:
        headers = {}
        if custom_api_key:
            headers["X-API-Key"] = custom_api_key
        elif use_jwt:
            token = st.session_state.get(StateKeys.JWT_TOKEN)
            if token:
                headers["Authorization"] = f"Bearer {token}"
        return headers

    @staticmethod
    def _handle_response(response: requests.Response) -> Dict[str, Any]:
        try:
            data = response.json()
        except Exception:
            data = {"detail": response.text or f"HTTP {response.status_code}"}

        if not response.ok:
            error_msg = data.get("detail", str(data)) if isinstance(data, dict) else str(data)
            raise Exception(f"API Error ({response.status_code}): {error_msg}")
        return data

    # -------------------------------------------------------------------------
    # Authentication & User
    # -------------------------------------------------------------------------
    @classmethod
    def register(cls, name: str, email: str, password: str) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/auth/register"
        resp = requests.post(url, json={"name": name, "email": email, "password": password})
        return cls._handle_response(resp)

    @classmethod
    def login(cls, email: str, password: str) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/auth/login"
        resp = requests.post(url, json={"email": email, "password": password})
        return cls._handle_response(resp)

    @classmethod
    def get_me(cls) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/auth/me"
        resp = requests.get(url, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # Vendors (Super Admin)
    # -------------------------------------------------------------------------
    @classmethod
    def create_vendor(cls, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/vendors"
        payload = {"name": name, "description": description}
        resp = requests.post(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def get_all_vendors(cls) -> List[Dict[str, Any]]:
        url = f"{cls.get_base_url()}/vendors"
        resp = requests.get(url, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def get_vendor(cls, vendor_id: str) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/vendors/{vendor_id}"
        resp = requests.get(url, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # Workspaces
    # -------------------------------------------------------------------------
    @classmethod
    def create_workspace(cls, vendor_id: str, name: str, description: Optional[str] = None, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/workspaces"
        payload = {
            "vendor_id": vendor_id,
            "name": name,
            "description": description,
            "system_prompt": system_prompt
        }
        resp = requests.post(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def get_vendor_workspaces(cls, vendor_id: str) -> List[Dict[str, Any]]:
        url = f"{cls.get_base_url()}/workspaces/vendor/{vendor_id}"
        resp = requests.get(url, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def update_workspace_prompt(cls, workspace_id: str, system_prompt: str) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/workspaces/{workspace_id}/prompt"
        payload = {"system_prompt": system_prompt}
        resp = requests.patch(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # Documents (Knowledge Ingestion)
    # -------------------------------------------------------------------------
    @classmethod
    def upload_document_file(cls, workspace_id: str, vendor_id: str, file_name: str, file_bytes: bytes) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/documents/upload"
        headers = cls._headers(use_jwt=True)
        files = {"file": (file_name, file_bytes)}
        data = {"workspace_id": workspace_id, "vendor_id": vendor_id}
        resp = requests.post(url, files=files, data=data, headers=headers)
        return cls._handle_response(resp)

    @classmethod
    def upload_json_document(cls, workspace_id: str, vendor_id: str, page_content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/documents/upload/json"
        payload = {
            "workspace_id": workspace_id,
            "vendor_id": vendor_id,
            "pageContent": page_content,
            "metadata": metadata or {}
        }
        resp = requests.post(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # API Keys
    # -------------------------------------------------------------------------
    @classmethod
    def create_api_key(cls, workspace_id: str, name: str) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/api-keys"
        payload = {"workspace_id": workspace_id, "name": name}
        resp = requests.post(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # Authenticated Workspace Chat
    # -------------------------------------------------------------------------
    @classmethod
    def ask_chat(cls, workspace_id: str, question: str, model_family: str, model_name: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/chat"
        payload = {
            "workspace_id": workspace_id,
            "question": question,
            "model_family": model_family,
            "model_name": model_name,
            "session_id": session_id
        }
        resp = requests.post(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # Public Chat (X-API-Key)
    # -------------------------------------------------------------------------
    @classmethod
    def ask_public_chat(cls, api_key: str, question: str, model_family: str = "gemini", model_name: str = "gemini-2.5-flash", session_id: Optional[str] = None) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/v1/public/chat"
        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        payload = {
            "question": question,
            "model_family": model_family,
            "model_name": model_name,
            "session_id": session_id
        }
        resp = requests.post(url, json=payload, headers=headers)
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # Global Modules
    # -------------------------------------------------------------------------
    @classmethod
    def get_all_modules(cls) -> List[Dict[str, Any]]:
        url = f"{cls.get_base_url()}/modules"
        resp = requests.get(url, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def create_module(cls, name: str, description: Optional[str] = None, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/modules"
        payload = {"name": name, "description": description, "system_prompt": system_prompt}
        resp = requests.post(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def grant_vendor_module_access(cls, module_id: str, vendor_id: str) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/modules/{module_id}/grant"
        payload = {"vendor_id": vendor_id}
        resp = requests.post(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def upload_module_json(cls, module_id: str, page_content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/modules/{module_id}/documents/json"
        payload = {"pageContent": page_content, "metadata": metadata or {}}
        resp = requests.post(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def upload_module_schema(cls, module_id: str, table_name: str, schema_ddl: str, description: str = "", relationships: str = "") -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/modules/{module_id}/documents/schema"
        payload = {
            "table_name": table_name,
            "schema_ddl": schema_ddl,
            "description": description,
            "relationships": relationships
        }
        resp = requests.post(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # Analytics & Text-to-SQL Chat
    # -------------------------------------------------------------------------
    @classmethod
    def analytics_chat(cls, vendor_id: str, module_id: str, question: str, model_family: Optional[str] = "gemini", model_name: Optional[str] = "gemini-2.5-flash", session_id: Optional[str] = None) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/analytics-chat"
        payload = {
            "vendor_id": vendor_id,
            "module_id": module_id,
            "question": question,
            "model_family": model_family,
            "model_name": model_name,
            "session_id": session_id
        }
        resp = requests.post(url, json=payload)
        return cls._handle_response(resp)

    @classmethod
    def test_analytics_db(cls) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/analytics-chat/db-test"
        resp = requests.get(url)
        return cls._handle_response(resp)

    @classmethod
    def internal_module_chat(cls, vendor_id: str, module_id: str, question: str, model_family: Optional[str] = "gemini", model_name: Optional[str] = "gemini-2.5-flash", session_id: Optional[str] = None) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/module-chat"
        payload = {
            "vendor_id": vendor_id,
            "module_id": module_id,
            "question": question,
            "model_family": model_family,
            "model_name": model_name,
            "session_id": session_id
        }
        resp = requests.post(url, json=payload)
        return cls._handle_response(resp)

    @classmethod
    def public_module_chat(cls, api_key: str, vendor_id: str, module_id: str, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/v1/public/module-chat"
        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        payload = {
            "vendor_id": vendor_id,
            "module_id": module_id,
            "question": question,
            "session_id": session_id
        }
        resp = requests.post(url, json=payload, headers=headers)
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # Chat History
    # -------------------------------------------------------------------------
    @classmethod
    def get_vendor_sessions(cls, vendor_id: str) -> List[Dict[str, Any]]:
        url = f"{cls.get_base_url()}/history/sessions/{vendor_id}"
        resp = requests.get(url)
        data = cls._handle_response(resp)
        return data.get("sessions", [])

    @classmethod
    def get_session_messages(cls, session_id: str) -> List[Dict[str, Any]]:
        url = f"{cls.get_base_url()}/history/session/{session_id}"
        resp = requests.get(url)
        data = cls._handle_response(resp)
        return data.get("messages", [])

    # -------------------------------------------------------------------------
    # Billing & Token Usage
    # -------------------------------------------------------------------------
    @classmethod
    def get_billing_stats(cls, vendor_id: str) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/billing/{vendor_id}"
        resp = requests.get(url, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def update_vendor_status(cls, vendor_id: str, status: str) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/billing/{vendor_id}/status"
        payload = {"status": status}
        resp = requests.put(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # AI Model Registry
    # -------------------------------------------------------------------------
    @classmethod
    def list_models(cls) -> List[Dict[str, Any]]:
        url = f"{cls.get_base_url()}/models"
        resp = requests.get(url)
        return cls._handle_response(resp)

    @classmethod
    def create_model(cls, model_family: str, model_name: str, provider: str, display_name: str) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/models"
        payload = {
            "model_family": model_family,
            "model_name": model_name,
            "provider": provider,
            "display_name": display_name
        }
        resp = requests.post(url, json=payload, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def delete_model(cls, model_id: str) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/models/{model_id}"
        resp = requests.delete(url, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    # -------------------------------------------------------------------------
    # APM Logs & Health
    # -------------------------------------------------------------------------
    @classmethod
    def health_check(cls) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/health"
        resp = requests.get(url)
        return cls._handle_response(resp)

    @classmethod
    def get_logs(cls, vendor_id: Optional[str] = None, workspace_id: Optional[str] = None, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if vendor_id:
            url = f"{cls.get_base_url()}/logs/vendor/{vendor_id}"
        elif workspace_id:
            url = f"{cls.get_base_url()}/logs/workspace/{workspace_id}"
        elif session_id:
            url = f"{cls.get_base_url()}/logs/session/{session_id}"
        else:
            url = f"{cls.get_base_url()}/logs"
        resp = requests.get(url, headers=cls._headers(use_jwt=True))
        return cls._handle_response(resp)

    @classmethod
    def test_redis(cls) -> Dict[str, Any]:
        url = f"{cls.get_base_url()}/test-redis"
        resp = requests.get(url)
        return cls._handle_response(resp)
