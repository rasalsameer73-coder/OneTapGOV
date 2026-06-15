from services.supabase_service import supabase

class FarmerService:
    @staticmethod
    def get_profile(user_id: str):
        res = supabase.table("farmer_profile").select("*").eq("user_id", user_id).single().execute()
        return res.data if res.data else {}

    @staticmethod
    def update_profile(user_id: str, data: dict):
        return supabase.table("farmer_profile").update(data).eq("user_id", user_id).execute()
