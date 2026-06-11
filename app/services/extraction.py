import asyncio
import re
from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.identity import AIUsageLog
from app.repositories.operations import OperationsRepository
from app.schemas.extraction import ExtractedProfile, ExtractionResponse
from app.utils.sanitization import sanitize_text
from app.services.translation import get_translation_provider
from structlog import get_logger

logger = get_logger()


class ExtractionProvider(ABC):
    @abstractmethod
    async def extract(self, text: str) -> tuple[dict, dict]:
        """Return structured fields and usage metadata."""
        raise NotImplementedError


class LocalStructuredExtractionProvider(ExtractionProvider):
    """Deterministic development adapter; replace through the provider interface."""

    STATES = (
        "Maharashtra",
        "Karnataka",
        "Gujarat",
        "Rajasthan",
        "Tamil Nadu",
        "Kerala",
        "Delhi",
        "Uttar Pradesh",
        "Madhya Pradesh",
        "West Bengal",
        "Punjab",
        "Haryana",
        "Odisha",
        "Bihar",
        "Assam",
    )
    COURSES = (
        "engineering",
        "medicine",
        "medical",
        "b.tech",
        "btech",
        "mba",
        "b.sc",
        "bsc",
        "diploma",
        "phd",
    )
    CATEGORIES = ("SC", "ST", "OBC", "EWS", "General")

    async def extract(self, text: str) -> tuple[dict, dict]:
        lowered = text.casefold()
        result: dict = {}
        confidence: dict[str, float] = {}
        for state in self.STATES:
            if state.casefold() in lowered:
                result["state"] = state
                confidence["state"] = 0.98
                break
        income = self._income(text)
        if income is not None:
            result["income"] = income
            confidence["income"] = 0.94
        for course in self.COURSES:
            if course in lowered:
                result["course"] = course.title()
                result["is_student"] = "student" in lowered or course in lowered
                confidence["course"] = 0.9
                confidence["is_student"] = 0.85
                break
        for category in self.CATEGORIES:
            if re.search(rf"\b{re.escape(category)}\b", text, re.IGNORECASE):
                result["category"] = category.upper() if category != "General" else category
                confidence["category"] = 0.9
                break
        usage = {
            "input_tokens": max(1, len(text.split())),
            "output_tokens": max(1, len(result) * 4),
            "confidence": confidence,
        }
        return result, usage

    @staticmethod
    def _income(text: str) -> Decimal | None:
        lakh = re.search(
            r"(?:₹|rs\.?|inr)?\s*([\d,.]+)\s*(?:lakh|lakhs|lac|lacs)\b",
            text,
            re.IGNORECASE,
        )
        if lakh:
            return Decimal(lakh.group(1).replace(",", "")) * Decimal("100000")
        annual = re.search(
            r"(?:income|earning|earns?)(?:\s+is|\s+of)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+)",
            text,
            re.IGNORECASE,
        )
        return Decimal(annual.group(1).replace(",", "")) if annual else None


class OpenAIExtractionProvider(ExtractionProvider):
    """Adapter for OpenAI/Gemini-style LLMs. Attempts to use `openai` package
    or raises a clear error if it's not installed. This provider is intentionally
    lightweight; replace or extend as needed for production usage.
    """

    def __init__(self):
        try:
            import openai

            self._client = openai
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("OpenAI client not available; install openai package") from exc

    async def extract(self, text: str) -> tuple[dict, dict]:
        # Minimal example using ChatCompletion; adapt prompts and parsing for production.
        prompt = f"Extract structured profile fields from the following text:\n\n{text}\n\nReturn JSON with keys like state, income, course, category, is_student."  # noqa: E501
        response = self._client.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
        )
        content = response.choices[0].message.content
        # Try to parse JSON from the model output; fall back to empty dict.
        import json

        try:
            parsed = json.loads(content)
        except Exception:
            parsed = {}
        usage = {
            "input_tokens": response.usage.get("prompt_tokens", 1),
            "output_tokens": response.usage.get("completion_tokens", 1),
            "confidence": {},
        }
        return parsed, usage


class AIExtractionService:
    def __init__(
        self,
        session: AsyncSession,
        provider: ExtractionProvider | None = None,
    ) -> None:
        self.session = session
        self.operations = OperationsRepository(session)
        # Choose provider based on configuration if not explicitly provided
        if provider is not None:
            self.provider = provider
        else:
            from app.core.config import settings

            if settings.ai_provider and settings.ai_provider.lower() in ("openai", "gpt", "gemini"):
                try:
                    self.provider = OpenAIExtractionProvider()
                except Exception:
                    # Fall back to local structured provider when external client is unavailable
                    self.provider = LocalStructuredExtractionProvider()
            else:
                self.provider = LocalStructuredExtractionProvider()

    async def extract(self, user_id: UUID, text: str) -> ExtractionResponse:
        # Optionally translate input to English before extraction
        translation_provider = get_translation_provider()
        translated_text, detected_lang = translation_provider.translate_to_english(text)
        clean_text = sanitize_text(translated_text)
        request_id = str(uuid4())
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                raw, usage = await self.provider.extract(clean_text)
                logger.info("ai.extract.success", user_id=str(user_id), provider=settings.ai_provider, model=settings.ai_model, request_id=request_id)
                validated = ExtractedProfile.model_validate(raw)
                cost = self._cost(usage["input_tokens"], usage["output_tokens"])
                await self.operations.add(
                    AIUsageLog(
                        user_id=user_id,
                        provider=settings.ai_provider,
                        model=settings.ai_model,
                        input_tokens=usage["input_tokens"],
                        output_tokens=usage["output_tokens"],
                        estimated_cost=cost,
                        request_id=request_id,
                        status="success",
                    )
                )
                await self.session.commit()
                return ExtractionResponse(
                    extracted=validated,
                    confidence=usage.get("confidence", {}),
                    provider=settings.ai_provider,
                    model=settings.ai_model,
                    request_id=request_id,
                )
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep(0.1 * (2**attempt))
        await self.operations.add(
            AIUsageLog(
                user_id=user_id,
                provider=settings.ai_provider,
                model=settings.ai_model,
                input_tokens=max(1, len(clean_text.split())),
                output_tokens=0,
                estimated_cost=0,
                request_id=request_id,
                status="failed",
                error_message=str(last_error)[:2000],
            )
        )
        await self.session.commit()
        raise RuntimeError("AI extraction failed after retries") from last_error

    @staticmethod
    def _cost(input_tokens: int, output_tokens: int) -> Decimal:
        amount = (
            Decimal(str(input_tokens)) / 1000
            * Decimal(str(settings.ai_cost_per_1k_input_tokens))
            + Decimal(str(output_tokens))
            / 1000
            * Decimal(str(settings.ai_cost_per_1k_output_tokens))
        )
        return amount.quantize(Decimal("0.000001"))

