# Centralised AI Service (Multi-Vendor RAG Platform)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)

A highly scalable, multi-tenant AI backend designed to act as the "Central Brain" for proprietary software ecosystems (e.g., Payroll, CRM, HRMS). It provides a robust Retrieval-Augmented Generation (RAG) pipeline allowing third-party vendors and internal clients to intelligently query vast knowledge bases.

---

## 🚀 Key Features

* **Global Module Architecture**: Super Admins curate centralized knowledge bases (Modules). Vendors are granted access dynamically, ensuring strict security while saving massive infrastructure costs by eliminating siloed databases.
* **Hybrid Conversational Memory**: 
  * **Short-Term (Redis)**: Lightning-fast sliding window cache (2-hour TTL) injected directly into LLM prompts.
  * **Long-Term (MongoDB)**: Permanent archiving of all chat logs for analytics.
  * **Auto-Rehydration**: Seamlessly restores context into Redis when a user resumes a chat days later.
* **Multi-LLM Asynchronous Router**: Dynamically routes prompts to different LLMs (Google Gemini 2.5 Flash, Groq Llama-3) based on payload configuration. Fully non-blocking async architecture.
* **Dual-Authentication Chat Layers**:
  * **Internal (`/module-chat`)**: Tokenless, JWT-bypassed internal endpoint optimized for server-to-server or authenticated CRM integrations.
  * **Public (`/v1/public/module-chat`)**: Strict rate-limited, billable endpoints secured via `X-API-Key` for external developer integrations.
* **Custom APM & Zero-Blocking Analytics**: A proprietary background `deque` worker processes logs, exceptions, and latency metrics directly into MongoDB without stalling the FastAPI event loop.

---

## 🏗️ Architecture Stack

* **Framework**: FastAPI (Python 3.12+)
* **Vector Store**: Supabase (PostgreSQL with `pgvector`)
* **Primary Database**: MongoDB (Users, API Keys, APM Logs, Chat History)
* **Hot Cache**: Upstash Redis (Rate limiting, Short-term memory)
* **Embeddings**: Google Generative AI Text Embeddings
* **LLM Providers**: Google Gemini, Groq

---

## ⚙️ Local Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-org/multi-vendor.git
cd multi-vendor
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
# MongoDB
MONGO_URI=mongodb+srv://...

# Supabase (Vector Store)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Redis
REDIS_URL=rediss://default:password@upstash-url:port

# LLM Providers
GEMINI_API_KEY=your-google-gemini-key
GROQ_API_KEY=your-groq-key
```

### 5. Run the Server
```bash
uvicorn main:app --reload
```
The server will start on `http://127.0.0.1:8000`.

---

## 📖 API Documentation

Once the server is running, you can access the automatic interactive API documentation:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Core Endpoints

#### Module Management (Super Admin)
- `POST /modules` - Create a new Global Module.
- `POST /modules/{module_id}/documents/json` - Ingest raw JSON knowledgebases into Supabase pgvector.
- `POST /modules/{module_id}/grant` - Grant a Vendor ID access to a specific Module.

#### Chat Interfaces
- `POST /module-chat` - Internal RAG querying endpoint.
- `POST /v1/public/module-chat` - External, API-key secured RAG endpoint.

---

## 🛡️ Security

This platform strictly segregates tenant data. Vector queries are strictly filtered at the Supabase database layer using `workspace_id` matching, preventing data leakage across Modules. Vendors are verified via MongoDB mapping (`VendorAccessRepository`) before any embedding retrieval occurs.
