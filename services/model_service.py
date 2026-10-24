import uuid
from datetime import datetime, timezone
from repositories.model_repository import ModelRepository

class ModelService:
    @staticmethod
    async def create_model(payload, user):
        existing = await ModelRepository.get_by_name_and_family(payload.model_name, payload.model_family)
        if existing:
            raise ValueError("Model with this name and family already exists")

        model_data = {
            "model_id": str(uuid.uuid4()),
            "model_family": payload.model_family,
            "model_name": payload.model_name,
            "provider": payload.provider,
            "display_name": payload.display_name,
            "created_by": user["sub"] if user and "sub" in user else "SYSTEM",
            "created_at": datetime.now(timezone.utc),
            "updated_by": None,
            "updated_at": None
        }

        await ModelRepository.create(model_data)
        
        model_data.pop("_id", None)
        return model_data

    @staticmethod
    async def get_all_models():
        models = await ModelRepository.get_all()
        for m in models:
            m.pop("_id", None)
        return models

    @staticmethod
    async def get_model(model_id: str):
        model = await ModelRepository.get_by_id(model_id)
        if not model:
            raise ValueError("Model not found")
        model.pop("_id", None)
        return model

    @staticmethod
    async def update_model(model_id: str, payload, user):
        model = await ModelRepository.get_by_id(model_id)
        if not model:
            raise ValueError("Model not found")

        update_data = {k: v for k, v in payload.dict(exclude_unset=True).items()}
        if update_data:
            update_data["updated_by"] = user["sub"]
            update_data["updated_at"] = datetime.now(timezone.utc)
            await ModelRepository.update(model_id, update_data)
            
        updated_model = await ModelRepository.get_by_id(model_id)
        updated_model.pop("_id", None)
        return updated_model

    @staticmethod
    async def delete_model(model_id: str):
        model = await ModelRepository.get_by_id(model_id)
        if not model:
            raise ValueError("Model not found")
        await ModelRepository.delete(model_id)
        return {"message": "Model deleted successfully"}
