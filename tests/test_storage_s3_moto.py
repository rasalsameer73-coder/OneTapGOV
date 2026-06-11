import pytest


def test_s3_upload_with_moto(monkeypatch, tmp_path):
    moto = pytest.importorskip('moto')
    boto3 = pytest.importorskip('boto3')
    from moto import mock_s3
    import importlib
    from app.core import config

    @mock_s3
    def _inner():
        # create bucket
        boto3.client('s3').create_bucket(Bucket='test-bucket')

        # ensure settings point to the test bucket
        monkeypatch.setattr(config.settings, 'aws_s3_bucket', 'test-bucket', raising=False)

        storage = importlib.reload(importlib.import_module('app.services.storage'))
        prov = storage.S3StorageProvider()

        class Stream:
            def read(self):
                return b'hello-world'

        key, url = prov.upload('hello.txt', Stream())
        assert key == 's3://test-bucket/hello.txt'
        assert 'test-bucket' in url

    _inner()
