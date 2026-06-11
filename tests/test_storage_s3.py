import sys
import importlib
import types


def test_s3_upload_calls_boto3(monkeypatch, tmp_path):
    calls = {}

    class FakeClient:
        def put_object(self, Bucket, Key, Body):
            calls['Bucket'] = Bucket
            calls['Key'] = Key
            calls['Body'] = Body

    def fake_client_factory(*args, **kwargs):
        return FakeClient()

    fake_boto3 = types.SimpleNamespace(client=fake_client_factory)
    monkeypatch.setitem(sys.modules, 'boto3', fake_boto3)

    # patch module-level settings before importing storage
    from app.core import config
    original_settings = config.settings
    fake_settings = types.SimpleNamespace(aws_s3_bucket='mybucket', aws_access_key_id=None, aws_secret_access_key=None, aws_region=None)
    monkeypatch.setattr(config, 'settings', fake_settings, raising=True)

    storage = importlib.reload(importlib.import_module('app.services.storage'))
    prov = storage.S3StorageProvider()
    # restore storage module to reference original settings to avoid leaking into other tests
    import app.services.storage as storage_mod
    storage_mod.settings = original_settings

    class Stream:
        def read(self):
            return b'data-bytes'

    storage_key, public_url = prov.upload('file.txt', Stream())
    assert calls['Bucket'] == 'mybucket'
    assert calls['Key'] == 'file.txt'
    assert calls['Body'] == b'data-bytes'
    assert storage_key == 's3://mybucket/file.txt'
