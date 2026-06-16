from db.supabase import supabase


class VectorStoreService:

    @staticmethod
    def bulk_insert(
        rows: list
    ):

        return (
            supabase
            .table("rag_documents")
            .insert(rows)
            .execute()
        )