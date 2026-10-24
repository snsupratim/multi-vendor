import uuid
from datetime import datetime, timezone

from repositories.vendor_repository import VendorRepository


class VendorService:

    @staticmethod
    async def create_vendor(payload, user):
        raw_id = getattr(payload, "id", None) or getattr(payload, "vendor_id", None)
        vendor_id = raw_id.strip() if raw_id and isinstance(raw_id, str) and raw_id.strip() else str(uuid.uuid4())

        # Check if ID already exists
        existing_id = await VendorRepository.get_by_vendor_id(vendor_id)
        if existing_id:
            raise ValueError(f"Vendor with ID '{vendor_id}' already exists")

        existing = await VendorRepository.find_by_name(
            payload.name
        )

        if existing:
            raise ValueError(
                "Vendor already exists"
            )

        vendor = {
            "_id": vendor_id,
            "vendor_id": vendor_id,
            "name": payload.name,
            "description": payload.description,
            "status": "ACTIVE",
            "created_by": user["sub"],
            "created_at": datetime.now(
                timezone.utc
            )
        }

        await VendorRepository.create_vendor(
            vendor
        )

        return {
            "vendor_id": vendor["vendor_id"],
            "id": vendor["vendor_id"],
            "message": "Vendor created successfully"
        }

    @staticmethod
    async def get_all_vendors():

        vendors = await VendorRepository.get_all()

        response = []

        for vendor in vendors:
            vid = vendor.get("vendor_id") or str(vendor.get("_id"))
            response.append({
                "vendor_id": vid,
                "id": vid,
                "name": vendor["name"],
                "description": vendor.get("description"),
                "status": vendor.get("status", "ACTIVE")
            })

        return response

    @staticmethod
    async def get_vendor(vendor_id: str):

        vendor = await VendorRepository.get_by_vendor_id(
            vendor_id
        )

        if not vendor:
            raise ValueError(
                "Vendor not found"
            )

        vid = vendor.get("vendor_id") or str(vendor.get("_id"))
        return {
            "vendor_id": vid,
            "id": vid,
            "name": vendor["name"],
            "description": vendor.get("description"),
            "status": vendor.get("status", "ACTIVE")
        }