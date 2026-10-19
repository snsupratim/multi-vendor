# Multi-Tenant RAG & Analytics Platform - Streamlit Frontend

A production-ready, modular Streamlit frontend for the Multi-Tenant RAG & Analytics Platform.

## 🌟 Highlights
- **100% Complete API Coverage**: Dedicated UI for every endpoint in the backend.
- **Dynamic Text-to-SQL Visualizer**: Automatically renders Plotly Bar, Line, Pie charts, KPI Metric cards, Data Tables, and suggested follow-up chips from the LangGraph SQL Agent.
- **Tenant Context Persistence**: Effortlessly switch active Vendors, Workspaces, and Global Modules.
- **API Key & Widget Simulation**: Test public embeddable chat widgets with custom `X-API-Key` headers.
- **Super Admin Operations**: Onboard vendors, manage workspaces, ingest PDF/TXT/DOCX knowledge files, configure system prompts, and register AI models.
- **APM & Health Dashboard**: Live trace logs, Redis health ping, and backend health status.

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
cd frontend
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env` or leave defaults (`http://localhost:8000`):
```bash
cp .env.example .env
```

### 3. Launch Streamlit Application
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📂 Project Structure
```
frontend/
├── app.py                      # Main entrypoint and navigation router
├── requirements.txt            # Dependencies
├── config.py                   # Global constants and state keys
├── api_client.py               # Centralized HTTP client for all API routes
├── components/
│   ├── visualizer.py           # Plotly charts, dataframes, metrics & prompt chips
│   ├── navbar.py               # Top status bar showing active tenant and auth
│   └── alerts.py               # Notification callouts
└── views/
    ├── auth_view.py            # Login, register, profile inspection
    ├── vendors_view.py         # Vendor onboarding and list
    ├── workspaces_view.py      # Workspace creation & prompt editor
    ├── documents_view.py       # Knowledge base file & JSON ingestion
    ├── api_keys_view.py        # Workspace API key generator
    ├── workspace_chat_view.py  # Authenticated RAG chat
    ├── public_chat_view.py     # Public API widget simulator
    ├── modules_view.py         # Global modules, access grants, SQL DDL ingestion
    ├── analytics_chat_view.py  # Text-to-SQL Agent with interactive graphs
    ├── history_view.py         # Chat session browser and transcript reloader
    ├── billing_view.py         # Token quotas and block/unblock tenant controls
    ├── models_view.py          # AI Model registry
    └── logs_view.py            # APM logs and infrastructure health
```
