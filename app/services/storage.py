import os
import tempfile
from abc import ABC, abstractmethod
from typing import Tuple

from app.core.config import settings


class StorageProvider(ABC):
    @abstractmethod
    def upload(self, filename: str, stream) -> Tuple[str, str]:
        """Uploads file-like `stream`. Returns (storage_key, public_url_or_path)"""


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: str | None = None):
        self.base_dir = base_dir or os.path.join(tempfile.gettempdir(), "onetapgov_storage")
        os.makedirs(self.base_dir, exist_ok=True)

    def upload(self, filename: str, stream) -> Tuple[str, str]:
        dest = os.path.join(self.base_dir, filename)
        with open(dest, "wb") as out:
            # stream is a file-like object
            out.write(stream.read())
        return dest, dest


class SupabaseStorageProvider(StorageProvider):
    def __init__(self):
        try:
            from supabase import create_client

            self._client = create_client(settings.supabase_url or "", settings.supabase_publishable_key or "")
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Supabase client not available") from exc

    def upload(self, filename: str, stream) -> Tuple[str, str]:
        # Simplified sample: store in bucket named 'documents'
        data = stream.read()
        result = self._client.storage.from_('documents').upload(filename, data)
        if result.get('error'):
            raise RuntimeError(result['error'])
        public_url = self._client.storage.from_('documents').get_public_url(filename)['publicURL']
        storage_key = f"supabase://documents/{filename}"
        return storage_key, public_url


class S3StorageProvider(StorageProvider):
    def __init__(self):
        try:
            import boto3
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("boto3 not available") from exc
        self._client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id if hasattr(settings, 'aws_access_key_id') else None,
            aws_secret_access_key=settings.aws_secret_access_key if hasattr(settings, 'aws_secret_access_key') else None,
            region_name=getattr(settings, 'aws_region', None),
        )
        self.bucket = getattr(settings, 'aws_s3_bucket', None)

    def upload(self, filename: str, stream) -> Tuple[str, str]:
        data = stream.read()
        key = filename
        self._client.put_object(Bucket=self.bucket, Key=key, Body=data)
        storage_key = f"s3://{self.bucket}/{key}"
        public_url = f"https://{self.bucket}.s3.amazonaws.com/{key}"
        return storage_key, public_url


def get_storage_provider() -> StorageProvider:
    # Prefer Supabase, then S3, else local
    if settings.supabase_url and settings.supabase_publishable_key:
        try:
            return SupabaseStorageProvider()
        except Exception:
            pass
    if getattr(settings, 'aws_s3_bucket', None):
        try:
            return S3StorageProvider()
        except Exception:
            pass
    return LocalStorageProvider()
