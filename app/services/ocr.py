from abc import ABC, abstractmethod
from typing import Tuple
import importlib
import types
import os

from app.core.config import settings


class OCRProvider(ABC):
    @abstractmethod
    def extract_text(self, path: str) -> str:
        raise NotImplementedError


class LocalOCRProvider(OCRProvider):
    def extract_text(self, path: str) -> str:
        # No-op provider for environments without OCR installed
        return ""


class PytesseractOCRProvider(OCRProvider):
    def __init__(self):
        try:
            from PIL import Image
            import pytesseract
            # allow overriding the tesseract cmd via settings
            tcmd = getattr(settings, "tesseract_cmd", os.environ.get("TESSERACT_CMD"))
            if tcmd:
                try:
                    pytesseract.pytesseract.tesseract_cmd = tcmd
                except Exception:
                    # ignore if library layout differs
                    pass
            self._Image = Image
            self._pytesseract = pytesseract
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("pytesseract or PIL not available") from exc

    def extract_text(self, path: str) -> str:
        img = self._Image.open(path)
        try:
            return self._pytesseract.image_to_string(img)
        except Exception:
            # Fail gracefully and return empty string on OCR errors
            return ""


def _has_pytesseract_available() -> bool:
    try:
        importlib.import_module("pytesseract")
        importlib.import_module("PIL")
        return True
    except Exception:
        return False


def get_ocr_provider() -> OCRProvider:
    # If env explicitly disables OCR, return local no-op
    if getattr(settings, "ocr_enabled", None) is False:
        return LocalOCRProvider()
    if _has_pytesseract_available():
        try:
            return PytesseractOCRProvider()
        except Exception:
            return LocalOCRProvider()
    return LocalOCRProvider()
