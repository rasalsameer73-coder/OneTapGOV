from abc import ABC, abstractmethod

from app.core.config import settings


class TranslationProvider(ABC):
    @abstractmethod
    def translate_to_english(self, text: str) -> tuple[str, str]:
        """Return (translated_text, detected_language)"""


class NoOpTranslationProvider(TranslationProvider):
    def translate_to_english(self, text: str) -> tuple[str, str]:
        return text, "und"


class GoogleTransProvider(TranslationProvider):
    def __init__(self):
        try:
            from googletrans import Translator

            self._translator = Translator()
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("googletrans not available") from exc

    def translate_to_english(self, text: str) -> tuple[str, str]:
        result = self._translator.translate(text, dest="en")
        return result.text, result.src


def get_translation_provider() -> TranslationProvider:
    if not getattr(settings, "ai_translation_enabled", False):
        return NoOpTranslationProvider()
    provider = (settings.ai_translation_provider or "none").lower()
    if provider in ("google", "googletrans"):
        try:
            return GoogleTransProvider()
        except Exception:
            return NoOpTranslationProvider()
    return NoOpTranslationProvider()
