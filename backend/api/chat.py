from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.supabase_service import supabase
from services.profile_service import ProfileService
from services.groq_service import GroqService
from config.basic_questions import BASIC_FIELDS, FIELD_DESCRIPTIONS
from config.farmer_questions import FARMER_FIELDS, FARMER_FIELD_DESCRIPTIONS
from config.student_questions import STUDENT_FIELDS, STUDENT_FIELD_DESCRIPTIONS
from config.women_questions import WOMEN_FIELDS, WOMEN_FIELD_DESCRIPTIONS
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


router = APIRouter(prefix="/chat", tags=["Chat"])
groq_service = GroqService()
profile_service = ProfileService()
security = HTTPBearer()


class ChatRequest(BaseModel):
    message: Optional[str] = None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
        
    # Call supabase to get user
    res = supabase.auth.get_user(token)
        
    if not res or not res.user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
            
    return res.user

def get_field_info(field_name: str):
    """Combines all field descriptions into one lookup."""
    all_descriptions = {
        **FIELD_DESCRIPTIONS,
        **FARMER_FIELD_DESCRIPTIONS,
        **STUDENT_FIELD_DESCRIPTIONS,
        **WOMEN_FIELD_DESCRIPTIONS
    }
    return all_descriptions.get(field_name, field_name)

@router.post("")
async def chat_endpoint(request: ChatRequest, user = Depends(get_current_user)):
    # 1. Fetch current profile
    profile_res = supabase.table("user_basic_info").select("*").eq("user_id", user.id).execute()
    
    if not profile_res.data:
        # Create initial record if missing
        supabase.table("user_basic_info").insert({"user_id": user.id}).execute()
        profile = {}
    else:
        profile = profile_res.data[0]

    # If basic is complete or sector is known, try to fetch sector-specific info
    sector = profile.get("sector")
    sector_table = profile_service.get_sector_table(sector)
    if sector_table:
        sector_res = supabase.table(sector_table).select("*").eq("user_id", user.id).execute()
        if sector_res.data:
            profile.update(sector_res.data[0])
    
    # 2. Identify current phase and missing field
    missing_field = profile_service.find_first_missing(profile, BASIC_FIELDS)
    phase = "basic"
    
    if not missing_field:
        # Basic is complete, check sector-specific fields
        sector = profile.get("sector")
        sector_fields = profile_service.get_sector_fields(sector)
        missing_field = profile_service.find_first_missing(profile, sector_fields)
        phase = "sector_specific" if sector_fields else "completed"

    # 3. Handle user response if provided
    if request.message and missing_field:
        field_desc = get_field_info(missing_field)
        extracted_data = await groq_service.extract_data(missing_field, field_desc, request.message)
        
        if extracted_data.get(missing_field):
            # Update profile in Supabase
            target_table = profile_service.get_table_name(missing_field, sector=profile.get("sector"))
            
            # For sector tables, ensure record exists
            if target_table != "user_basic_info":
                check_res = supabase.table(target_table).select("user_id").eq("user_id", user.id).execute()
                if not check_res.data:
                    # Initialize record with user_id and the extracted data
                    insert_data = {"user_id": user.id}
                    insert_data.update(extracted_data)
                    supabase.table(target_table).insert(insert_data).execute()
                else:
                    supabase.table(target_table).update(extracted_data).eq("user_id", user.id).execute()
            else:
                supabase.table(target_table).update(extracted_data).eq("user_id", user.id).execute()
            
            # Refresh profile and find NEXT missing field
            profile.update(extracted_data)
            
            # If sector was just updated, we might need to fetch its table too
            if missing_field == "sector":
                new_sector = extracted_data.get("sector")
                new_sector_table = profile_service.get_sector_table(new_sector)
                if new_sector_table:
                    sector_res = supabase.table(new_sector_table).select("*").eq("user_id", user.id).execute()
                    if sector_res.data:
                        profile.update(sector_res.data[0])

            # Re-evaluate missing field and phase after update
            missing_field = profile_service.find_first_missing(profile, BASIC_FIELDS)
            phase = "basic"
            
            if not missing_field:
                sector = profile.get("sector")
                sector_fields = profile_service.get_sector_fields(sector)
                missing_field = profile_service.find_first_missing(profile, sector_fields)
                phase = "sector_specific" if sector_fields else "completed"

    # 4. Check if profile is now fully complete
    if not missing_field:
        return {
            "status": "fully_completed",
            "question": "Thank you! Your profile is now complete. We have all the information needed to recommend the best schemes for you.",
            "profile": profile
        }
    
    # 5. Generate next question
    language = profile.get("preferred_language", "English")
    field_desc = get_field_info(missing_field)
    
    question = await groq_service.generate_question(
        field_name=missing_field,
        field_description=field_desc,
        profile=profile,
        language=language
    )
    
    return {
        "status": "asking",
        "phase": phase,
        "question": question,
        "missing_field": missing_field
    }
