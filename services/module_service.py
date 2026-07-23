from repositories.module_repository import ModuleRepository
from repositories.vendor_access_repository import VendorAccessRepository

class ModuleService:
    @staticmethod
    async def create_module(name: str, description: str = None, system_prompt: str = None):
        return await ModuleRepository.create_module(name, description, system_prompt)
        
    @staticmethod
    async def grant_vendor_access(vendor_id: str, module_id: str):
        await VendorAccessRepository.grant_access(vendor_id, module_id)

    @staticmethod
    async def get_all_modules():
        return await ModuleRepository.get_all_modules()
