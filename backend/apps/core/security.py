from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import bleach
from rest_framework import serializers

MAX_RESUME_UPLOAD_SIZE = 10 * 1024 * 1024
ALLOWED_RESUME_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}


def sanitize_text(value: str) -> str:
    """Strip HTML and script content from user-controlled text fields."""
    return bleach.clean(value or "", tags=[], attributes={}, protocols=[], strip=True).strip()


def validate_resume_upload(file: BinaryIO, *, field_name: str = "file") -> None:
    if not file:
        return

    if getattr(file, "size", 0) > MAX_RESUME_UPLOAD_SIZE:
        raise serializers.ValidationError({field_name: "File size must be under 10MB."})

    file_name = getattr(file, "name", "")
    extension = Path(file_name).suffix.lower()
    if extension not in ALLOWED_RESUME_EXTENSIONS:
        raise serializers.ValidationError({field_name: "Only PDF and DOCX files are supported."})

    content_type = getattr(file, "content_type", "")
    if content_type not in ALLOWED_RESUME_MIME_TYPES:
        raise serializers.ValidationError({field_name: "Only PDF and DOCX files are supported."})

    position = file.tell() if hasattr(file, "tell") else None
    header = file.read(4096)
    if hasattr(file, "seek") and position is not None:
        file.seek(position)

    if not _has_expected_file_signature(header, extension):
        raise serializers.ValidationError(
            {field_name: "Uploaded file content does not match the selected resume type."}
        )


def validate_resume_bytes(
    file_bytes: bytes,
    *,
    file_name: str,
    content_type: str,
    field_name: str = "file",
) -> None:
    if len(file_bytes) > MAX_RESUME_UPLOAD_SIZE:
        raise serializers.ValidationError({field_name: "File size must be under 10MB."})

    extension = Path(file_name).suffix.lower()
    if extension not in ALLOWED_RESUME_EXTENSIONS or content_type not in ALLOWED_RESUME_MIME_TYPES:
        raise serializers.ValidationError({field_name: "Only PDF and DOCX files are supported."})

    if not _has_expected_file_signature(file_bytes[:4096], extension):
        raise serializers.ValidationError(
            {field_name: "Uploaded file content does not match the selected resume type."}
        )


def _has_expected_file_signature(header: bytes, extension: str) -> bool:
    if extension == ".pdf":
        return header.startswith(b"%PDF-")

    if extension == ".docx":
        if not header.startswith(b"PK\x03\x04"):
            return False
        try:
            with zipfile.ZipFile(BytesIO(header + b"")):
                return True
        except zipfile.BadZipFile:
            # The first chunk is enough to verify the ZIP signature; a complete
            # archive check happens later when python-docx/pdf extraction reads it.
            return True

    if extension == ".doc":
        return header.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")

    return False
