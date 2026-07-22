# Migrate Hardcoded Model Registry to CRUD API

This plan outlines the steps to migrate the current hardcoded model registry (`services/model_registry.py`) into a database-backed CRUD API, as well as updating the chat payloads to accept `model_family` and `model_name`.

## User Review Required

> [!WARNING]
> **API Contract Change**
> The payload for `POST /chat` and `POST /v1/public/chat` will change from having a single `model` string field to requiring both `model_family` and `model_name` string fields.

## Open Questions

> [!IMPORTANT]
> 1. **Schema Definition**: I am proposing the following fields for a Model: `model_id`, `model_family` (e.g., `llama-3`), `model_name` (e.g., `llama-3.1-8b-instant`), `provider` (e.g., `groq`), `display_name`, plus audit fields (`created_at`, `updated_at`, `created_by`, `updated_by`). Does this accurately reflect what you want?
> 2. **Migration**: Would you like me to write a one-time setup script to insert the currently hardcoded models into your database, or will you just add them manually via the new `/models` API once it's created?

## Proposed Changes

---

### DB Layer & Schemas

#### [NEW] [model_schema.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/schemas/model_schema.py)
Create Pydantic schemas for the CRUD operations (`ModelCreate`, `ModelUpdate`, `ModelResponse`). `ModelResponse` will include audit fields (`created_at`, `updated_at`, `created_by`, `updated_by`).

#### [NEW] [model_repository.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/repositories/model_repository.py)
Create a MongoDB repository connecting to `db["models"]` to support `create`, `get_by_id`, `get_by_family_and_name`, `get_all`, `update`, and `delete`.

---

### Services Layer

#### [NEW] [model_service.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/services/model_service.py)
Implement business logic for creating, updating, listing, and deleting models. Ensure audit fields are populated automatically during creation and update based on the current user.

#### [MODIFY] [model_router.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/services/model_router.py)
Convert `generate` to an `async` function. It will query the `ModelRepository` by `model_family` and `model_name` to find the correct `provider` instead of reading from the hardcoded dictionary.

#### [MODIFY] [chat_service.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/services/chat_service.py)
Convert `generate_answer` to an `async` function to `await ModelRouter.generate(...)`. Update the method signature to accept `model_family` and `model_name`.

#### [MODIFY] [rag_service.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/services/rag_service.py)
Update `RAGService.ask` signature to accept `model_family` and `model_name`, and `await ChatService.generate_answer(...)`.

#### [DELETE] [model_registry.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/services/model_registry.py)
Delete the hardcoded dictionary completely.

---

### API Layer (Routers)

#### [MODIFY] [models.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/api/models.py)
Implement the full CRUD endpoints (`POST /models`, `GET /models`, `GET /models/{model_id}`, `PUT /models/{model_id}`, `DELETE /models/{model_id}`). All endpoints except `GET /models` will be protected by `require_super_admin` to prevent unauthorized model creation.

#### [MODIFY] [chat_schema.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/schemas/chat_schema.py)
Change `model` field to `model_family` and `model_name`.

#### [MODIFY] [public_chat_schema.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/schemas/public_chat_schema.py)
Change `model` field to `model_family` and `model_name`.

#### [MODIFY] [chat.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/api/chat.py)
Pass `payload.model_family` and `payload.model_name` to `RAGService.ask`.

#### [MODIFY] [public_chat.py](file:///c:/Users/SUPRATIM/Documents/GitHub/multi-vendor/api/public_chat.py)
Pass `payload.model_family` and `payload.model_name` to `RAGService.ask`. Ensure logging works with the new model name structure if necessary.

## Verification Plan

### Automated Tests
- N/A (We'll run `main.py` locally and verify no syntax or runtime errors occur on startup).

### Manual Verification
- We will ask the user to use Postman to:
  1. Create a model using `POST /models` with audit fields.
  2. Send a `POST /chat` request with the newly created model's `model_family` and `model_name`.
  3. Validate that the chat resolves and responds properly.
