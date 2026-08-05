from repositories.billing_repository import BillingRepository

class BillingService:
    
    @staticmethod
    async def check_access(vendor_id: str) -> bool:
        """
        Check if the vendor is active and allowed to make LLM queries.
        If they don't exist, they are auto-created as active.
        """
        billing_record = await BillingRepository.get_or_create_vendor_billing(vendor_id)
        return billing_record.get("status") == "active"
        
    @staticmethod
    async def log_usage(
        vendor_id: str, 
        session_id: str, 
        model_name: str, 
        prompt_tokens: int, 
        completion_tokens: int
    ):
        """
        Logs token usage to immutable audit trail and updates the vendor's aggregates.
        """
        return await BillingRepository.log_token_usage(
            vendor_id=vendor_id,
            session_id=session_id,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens
        )
        
    @staticmethod
    async def get_vendor_stats(vendor_id: str):
        """
        Returns total usage and the average queries per 1 million tokens.
        """
        record = await BillingRepository.get_or_create_vendor_billing(vendor_id)
        
        total_tokens = record.get("total_tokens", 0)
        total_queries = record.get("total_queries", 0)
        
        # Calculate queries per 1 million tokens
        if total_tokens > 0:
            queries_per_million = (1_000_000 / total_tokens) * total_queries
        else:
            queries_per_million = 0
            
        return {
            "vendor_id": vendor_id,
            "status": record.get("status"),
            "total_queries": total_queries,
            "total_prompt_tokens": record.get("total_prompt_tokens", 0),
            "total_completion_tokens": record.get("total_completion_tokens", 0),
            "total_tokens": total_tokens,
            "avg_queries_per_million_tokens": round(queries_per_million, 2)
        }
        
    @staticmethod
    async def update_vendor_status(vendor_id: str, status: str):
        if status not in ["active", "inactive"]:
            raise ValueError("Status must be 'active' or 'inactive'")
        # Ensure they exist first
        await BillingRepository.get_or_create_vendor_billing(vendor_id)
        return await BillingRepository.update_vendor_status(vendor_id, status)
