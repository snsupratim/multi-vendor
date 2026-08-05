import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuration
API_URL = "http://localhost:8000/analytics-chat"
VENDOR_ID = "6054690d-f545-43a9-83ab-d2435abfdeaf"
MODULE_ID = "6361cf82-2b1a-4570-b8fc-dfa2d456ca02"

st.set_page_config(page_title="Tek Anthem Analytics Demo", layout="wide")
st.title("📊 Tek Anthem - AI Analytics Chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.write(msg["content"])
        else:
            # Render AI Components
            for comp in msg["components"]:
                if comp["componentType"] == "TEXT":
                    st.markdown(f"**{comp['title']}**\n\n{comp['description']}")
                elif comp["componentType"] == "TABLE":
                    st.subheader(comp['title'])
                    if comp['description']: st.caption(comp['description'])
                    st.dataframe(pd.DataFrame(comp["data"]))
                elif comp["componentType"] == "GRAPH":
                    st.subheader(comp['title'])
                    if comp['description']: st.caption(comp['description'])
                    
                    df = pd.DataFrame(comp["data"])
                    chart_type = comp["config"].get("type", "bar")
                    x_axis = comp["config"].get("xAxis")
                    y_axis = comp["config"].get("yAxis")
                    
                    if chart_type == "bar":
                        st.plotly_chart(px.bar(df, x=x_axis, y=y_axis))
                    elif chart_type == "pie":
                        # For pie, xAxis is typically names, yAxis is values
                        st.plotly_chart(px.pie(df, names=x_axis, values=y_axis))
                    elif chart_type == "line":
                        st.plotly_chart(px.line(df, x=x_axis, y=y_axis))
                    else:
                        st.bar_chart(df.set_index(x_axis))

# Chat Input
if prompt := st.chat_input("Ask about your leaves..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Thinking and writing SQL..."):
            payload = {
                "vendor_id": VENDOR_ID,
                "module_id": MODULE_ID,
                "question": prompt,
                "model_family": "gemini",
                "model_name": "gemini-2.5-flash",
                "session_id": st.session_state.session_id
            }
            
            try:
                response = requests.post(API_URL, json=payload)
                data = response.json()
                
                # Save session ID for memory
                st.session_state.session_id = data.get("session_id")
                components = data.get("components", [])
                
                # Save to state
                st.session_state.messages.append({"role": "assistant", "components": components})
                
                # Force rerun to render new components neatly via the loop above
                st.rerun()
                
            except Exception as e:
                st.error(f"Failed to connect to backend: {str(e)}")
