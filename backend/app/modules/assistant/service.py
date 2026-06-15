from google import genai

from app.core.config import settings

from app.modules.assistant.schemas import (
    AssistantResponse,
)


class AssistantService:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    async def answer_question(
        self,
        question: str,
    ) -> AssistantResponse:

        prompt = f"""
You are OneTapGOV AI.

Answer questions related to Indian government schemes.

Question:
{question}

Provide clear and concise answers in simple language.
"""

        try:

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            return AssistantResponse(
                answer=response.text
                or "Sorry, I could not generate an answer."
            )

        except Exception as e:

            return AssistantResponse(
                answer=(
                    "Sorry, I am unable to answer your question "
                    "at the moment. Please try again later."
                )
            )