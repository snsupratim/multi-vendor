import streamlit as st
from typing import Optional

def show_error(message: str, exception: Optional[Exception] = None):
    """Displays a stylized error message with optional traceback expander."""
    st.error(f"❌ **Error:** {message}")
    if exception:
        with st.expander("Show Detailed Error"):
            st.exception(exception)

def show_success(message: str):
    """Displays a stylized success notification."""
    st.success(f"✅ **Success:** {message}")

def show_info(message: str):
    """Displays an informational note."""
    st.info(f"ℹ️ {message}")

def show_warning(message: str):
    """Displays a warning notification."""
    st.warning(f"⚠️ {message}")
