import os
from urllib.parse import quote

import httpx
from django.conf import settings


def _normalize_supabase_url(url: str) -> str:
    return url.rstrip("/").removesuffix("/rest/v1")


SUPABASE_URL = _normalize_supabase_url(
    getattr(settings, "SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
)
SUPABASE_SERVICE_ROLE_KEY = getattr(
    settings,
    "SUPABASE_SERVICE_ROLE_KEY",
    os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
)


def _require_storage_config() -> None:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set "
            "to use Supabase Storage."
        )


def _storage_url(path: str) -> str:
    return f"{SUPABASE_URL}/storage/v1/{path.lstrip('/')}"


def _headers(content_type: str | None = None) -> dict[str, str]:
    _require_storage_config()
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def _object_path(bucket_name: str, file_path: str) -> str:
    return f"{quote(bucket_name, safe='')}/{quote(file_path.strip('/'), safe='/')}"


def _raise_for_storage_status(response: httpx.Response) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ValueError(f"Supabase Storage error: {response.text}") from exc


def upload_file(bucket_name: str, file_path: str, file_obj, content_type: str) -> str:
    """
    Upload a file to a private Supabase Storage bucket through the server.
    """
    file_bytes = file_obj.read()
    response = httpx.post(
        _storage_url(f"object/{_object_path(bucket_name, file_path)}"),
        headers={**_headers(content_type), "x-upsert": "false"},
        content=file_bytes,
        timeout=30,
    )
    _raise_for_storage_status(response)
    return file_path


def get_signed_url(bucket_name: str, file_path: str, expiry_seconds: int = 3600) -> str:
    """
    Generate a short-lived signed URL for a private Supabase Storage object.
    """
    response = httpx.post(
        _storage_url(f"object/sign/{_object_path(bucket_name, file_path)}"),
        headers=_headers("application/json"),
        json={"expiresIn": expiry_seconds},
        timeout=30,
    )
    _raise_for_storage_status(response)
    data = response.json()
    signed_url = data.get("signedURL") or data.get("signed_url") or data.get("signedUrl", "")
    if signed_url.startswith("/"):
        return f"{SUPABASE_URL}{signed_url}"
    return signed_url


def download_file(bucket_name: str, file_path: str) -> bytes:
    response = httpx.get(
        _storage_url(f"object/{_object_path(bucket_name, file_path)}"),
        headers=_headers(),
        timeout=30,
    )
    _raise_for_storage_status(response)
    return response.content


def ensure_bucket(bucket_name: str, public: bool = False) -> bool:
    """
    Ensure a Storage bucket exists. Returns True when a bucket was created.
    """
    list_response = httpx.get(
        _storage_url("bucket"),
        headers=_headers(),
        timeout=30,
    )
    _raise_for_storage_status(list_response)
    buckets = list_response.json()
    bucket_names = {bucket.get("name") or bucket.get("id") for bucket in buckets}
    if bucket_name in bucket_names:
        return False

    create_response = httpx.post(
        _storage_url("bucket"),
        headers=_headers("application/json"),
        json={"id": bucket_name, "name": bucket_name, "public": public},
        timeout=30,
    )
    _raise_for_storage_status(create_response)
    return True


def delete_file(bucket_name: str, file_path: str) -> None:
    response = httpx.request(
        "DELETE",
        _storage_url(f"object/{quote(bucket_name, safe='')}"),
        headers=_headers("application/json"),
        json={"prefixes": [file_path]},
        timeout=30,
    )
    _raise_for_storage_status(response)
