import sys
import importlib
import types
from pathlib import Path


def test_local_provider_when_no_pytesseract(monkeypatch):
    # Ensure modules are not present
    monkeypatch.setitem(sys.modules, 'pytesseract', None)
    monkeypatch.setitem(sys.modules, 'PIL', None)
    mod = importlib.reload(importlib.import_module('app.services.ocr'))
    prov = mod.get_ocr_provider()
    assert prov.extract_text(str(Path("/no/such/file.png"))) == ""


def test_pytesseract_provider(monkeypatch, tmp_path):
    # Create fake PIL.Image and pytesseract modules
    fake_img = object()

    class FakeImageModule:
        @staticmethod
        def open(path):
            return fake_img

    class FakePytesseract:
        @staticmethod
        def image_to_string(img):
            if img is fake_img:
                return "detected text"
            return ""

    fake_pil = types.SimpleNamespace(Image=FakeImageModule)
    monkeypatch.setitem(sys.modules, 'PIL', fake_pil)
    monkeypatch.setitem(sys.modules, 'pytesseract', FakePytesseract)

    mod = importlib.reload(importlib.import_module('app.services.ocr'))
    prov = mod.get_ocr_provider()
    out = prov.extract_text(str(tmp_path / 'f.png'))
    assert out == "detected text"
