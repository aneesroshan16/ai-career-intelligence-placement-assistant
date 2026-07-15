"""
Storage abstraction for uploaded resume files (and future generated reports).
Local filesystem by default (zero setup for development); switches to
Supabase Storage transparently once SUPABASE_URL/SERVICE_ROLE_KEY are real
production credentials. Callers only ever see `upload()` / `get_url()`.
"""
from __future__ import annotations

import os
import uuid
from abc import ABC, abstractmethod

from app.core.config import get_settings


class StorageProvider(ABC):
    @abstractmethod
    async def upload(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        """Stores the file, returns a URL/path that `get_url` can resolve later."""
        raise NotImplementedError

    @abstractmethod
    def get_url(self, stored_path: str) -> str:
        raise NotImplementedError


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    async def upload(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        path = os.path.join(self.base_dir, unique_name)
        with open(path, "wb") as f:
            f.write(file_bytes)
        return path

    def get_url(self, stored_path: str) -> str:
        return f"file://{os.path.abspath(stored_path)}"


class SupabaseStorageProvider(StorageProvider):
    def __init__(self, supabase_url: str, service_role_key: str, bucket: str):
        self.base_url = supabase_url.rstrip("/")
        self.key = service_role_key
        self.bucket = bucket

    async def upload(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        import httpx

        unique_name = f"{uuid.uuid4().hex}_{filename}"
        object_path = f"{self.bucket}/{unique_name}"
        url = f"{self.base_url}/storage/v1/object/{object_path}"
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, content=file_bytes)
            resp.raise_for_status()
        return object_path

    def get_url(self, stored_path: str) -> str:
        return f"{self.base_url}/storage/v1/object/public/{stored_path}"


def get_storage_provider() -> StorageProvider:
    settings = get_settings()
    if settings.ENVIRONMENT == "local" or "your-project" in settings.SUPABASE_URL:
        return LocalStorageProvider(settings.LOCAL_STORAGE_DIR)
    return SupabaseStorageProvider(
        settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY, settings.SUPABASE_STORAGE_BUCKET
    )
