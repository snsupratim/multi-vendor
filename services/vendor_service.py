import uuid
from datetime import datetime, timezone

from repositories.vendor_repository import VendorRepository


class VendorService:

    @staticmethod
    async def create_vendor(payload, user):

        existing = await VendorRepository.find_by_name(
            payload.name
        )

        if existing:
            raise ValueError(
                "Vendor already exists"
            )

        vendor = {
            "vendor_id": str(uuid.uuid4()),
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
            "message": "Vendor created successfully"
        }

    @staticmethod
    async def get_all_vendors():

        vendors = await VendorRepository.get_all()

        response = []

        for vendor in vendors:

            response.append({
                "vendor_id": vendor["vendor_id"],
                "name": vendor["name"],
                "description": vendor.get("description"),
                "status": vendor["status"]
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

        return {
            "vendor_id": vendor["vendor_id"],
            "name": vendor["name"],
            "description": vendor.get("description"),
            "status": vendor["status"]
        }