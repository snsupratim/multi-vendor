import hashlib
import secrets
import uuid

from datetime import datetime, timezone

from repositories.api_key_repository import (
    ApiKeyRepository
)
from repositories.vendor_repository import VendorRepository
from repositories.workspace_repository import WorkspaceRepository

class ApiKeyService:

    @staticmethod
    async def create_key(payload, user):

    # Verify vendor exists
    #     vendor = await VendorRepository.get_by_vendor_id(
    #     payload.vendor_id
    # )

    #     if not vendor:
    #         raise ValueError(
    #         "Vendor not found"
    #     )

    # Verify workspace exists
        workspace = await WorkspaceRepository.get_by_workspace_id(
        payload.workspace_id
    )
        vendor_id = workspace["vendor_id"]

        if not workspace:
            raise ValueError(
            "Workspace not found"
        )

    # Verify workspace belongs to the vendor
        if workspace["vendor_id"] != vendor_id:
            raise ValueError(
            "Workspace does not belong to the specified vendor"
        )

        # if workspace.get("status") != "ACTIVE":
        #     raise ValueError("Workspace is not active")

    # Generate API key after validation
        raw_key = (
        "mv_live_" +
        secrets.token_urlsafe(32)
    )

        hashed = hashlib.sha256(
        raw_key.encode()
    ).hexdigest()

        api_key_id = str(uuid.uuid4())


        document = {

            "api_key_id": api_key_id,

            "name": payload.name,

            "key_prefix": "mv_live",

            "api_key_hash": hashed,

            "vendor_id": vendor_id,

            "workspace_id": payload.workspace_id,

            "status": "ACTIVE",

            "subscription": {

    "tier": "FREE",

    "requests_per_minute": 20,

    "requests_per_hour": 500,

    "input_tokens_per_day": 100000,

    "output_tokens_per_day": 100000,

    "monthly_cost_limit_usd": 10
},

            "created_by": user["sub"],

            "created_at": datetime.now(
                timezone.utc
            ),

            "expires_at": None,

            "last_used_at": None
        }

        await ApiKeyRepository.create(
            document
        )

        return {

            "api_key": raw_key,

            "api_key_id": api_key_id
        }

    @staticmethod
    async def validate_key(raw_key: str):

        hashed = hashlib.sha256(
        raw_key.encode()
    ).hexdigest()

        api_key = await (
        ApiKeyRepository.get_by_hash(
            hashed
        )
    )

        return api_key