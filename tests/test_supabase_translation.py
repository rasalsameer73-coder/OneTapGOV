import importlib
import types
import sys
from app.core import config


def test_translation_noop(monkeypatch):
    translation = importlib.reload(importlib.import_module('app.services.translation'))
    prov = translation.get_translation_provider()
    out, lang = prov.translate_to_english('hola')
    # default NoOp should return same input and None/empty detected language
    assert out == 'hola'


def test_supabase_provider_mock(monkeypatch):
    # Mock supabase client
    fake_client = types.SimpleNamespace(storage=types.SimpleNamespace(from_=lambda bucket: types.SimpleNamespace(upload=lambda k, d: {"error": None}, get_public_url=lambda k: {"publicURL": "https://supabase/test/"})))
    fake_create = lambda url, key: fake_client
    monkeypatch.setitem(sys.modules, 'supabase', types.SimpleNamespace(create_client=fake_create))
    # Ensure settings for supabase are present
    monkeypatch.setattr(config.settings, 'supabase_url', 'https://x', raising=False)
    monkeypatch.setattr(config.settings, 'supabase_publishable_key', 'pubkey', raising=False)

    storage_mod = importlib.reload(importlib.import_module('app.services.storage'))
    prov = storage_mod.SupabaseStorageProvider()

    class Stream:
        def read(self):
            return b'data'

    key, url = prov.upload('f.txt', Stream())
    assert key.startswith('supabase://')
