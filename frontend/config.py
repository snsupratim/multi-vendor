import os
from dotenv import load_dotenv

load_dotenv()

# Backend Configuration
DEFAULT_API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DEFAULT_MODEL_FAMILY = os.getenv("DEFAULT_MODEL_FAMILY", "gemini")
DEFAULT_MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", "gemini-2.5-flash")

# Session State Keys
class StateKeys:
    API_BASE_URL = "api_base_url"
    JWT_TOKEN = "jwt_token"
    USER_INFO = "user_info"
    API_KEY = "api_key"
    ACTIVE_VENDOR_ID = "active_vendor_id"
    ACTIVE_WORKSPACE_ID = "active_workspace_id"
    ACTIVE_MODULE_ID = "active_module_id"
    CHAT_MESSAGES = "chat_messages"
    ANALYTICS_MESSAGES = "analytics_messages"
    ACTIVE_SESSION_ID = "active_session_id"
    SELECTED_MODEL_FAMILY = "selected_model_family"
    SELECTED_MODEL_NAME = "selected_model_name"
