import os
import json
from groq import Groq
from prompts.question_prompt import QUESTION_PROMPT
from prompts.extraction_prompt import EXTRACTION_PROMPT

class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        # Using a highly capable Llama 3 model available on Groq
        self.model_id = "llama-3.3-70b-versatile"

    async def generate_question(self, field_name: str, field_description: str, profile: dict, language: str = "English"):
        context = "\n".join([f"{k}: {v}" for k, v in profile.items() if v])
        prompt = QUESTION_PROMPT.format(
            field_name=field_name,
            field_description=field_description,
            profile_context=context or "New user, no data yet.",
            language=language
        )
        
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    async def extract_data(self, field_name: str, field_description: str, user_message: str):
        prompt = EXTRACTION_PROMPT.format(
            field_name=field_name,
            field_description=field_description,
            user_message=user_message
        )
        
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {field_name: None}
