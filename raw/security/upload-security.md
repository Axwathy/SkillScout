---
type: security
title: "File Upload Security"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [security, recruitment/uploads]
---

## Overview

The recruitment SaaS accepts file uploads primarily for candidate resumes. File uploads are a significant attack surface — they can introduce malware, server-side exploits, storage abuse, and data exfiltration vectors. This document defines the defense-in-depth strategy for securing all file upload operations.

For the resume processing pipeline, see [[resume-parser|Resume Parser]]. For the upload feature, see [[sprint-05-resume-upload|Sprint 5 — Resume Upload & Storage]].

## Allowed File Types

| Extension | MIME Type | Max Size | Use Case |
|---|---|---|---|
| `.pdf` | `application/pdf` | 10 MB | Resume (most common format) |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | 10 MB | Resume (Word format) |
| `.doc` | `application/msword` | 10 MB | Resume (legacy Word format) |

All other file types are **rejected at upload time** with a 415 Unsupported Media Type response.

## Validation Pipeline

File validation follows a multi-layer approach — each layer catches different attack vectors:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Extension   │ →  │  MIME Type   │ →  │  File Size   │ →  │   Content    │
│  Validation  │    │  Validation  │    │  Validation  │    │  Inspection  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       ↓ reject            ↓ reject           ↓ reject           ↓ reject
   Wrong ext          MIME mismatch       > 10 MB           Malicious content
```

### Django Implementation

```python
# validators/upload.py

import magic
import os
from django.core.exceptions import ValidationError

ALLOWED_TYPES = {
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_upload(file) -> None:
    """Multi-layer file upload validation."""

    # Layer 1: File size check (before reading content)
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f'File size ({file.size / 1024 / 1024:.1f} MB) exceeds '
            f'maximum allowed size ({MAX_FILE_SIZE / 1024 / 1024:.0f} MB).'
        )

    # Layer 2: Extension check
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = [e for exts in ALLOWED_TYPES.values() for e in exts]
    if ext not in allowed_extensions:
        raise ValidationError(
            f'File extension "{ext}" is not allowed. '
            f'Accepted formats: {", ".join(allowed_extensions)}'
        )

    # Layer 3: MIME type validation (magic bytes, not Content-Type header)
    file.seek(0)
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)

    if mime not in ALLOWED_TYPES:
        raise ValidationError(
            f'File content type "{mime}" does not match an allowed type. '
            f'The file may be corrupted or mislabeled.'
        )

    # Layer 4: Extension-MIME consistency check
    if ext not in ALLOWED_TYPES[mime]:
        raise ValidationError(
            f'File extension "{ext}" does not match content type "{mime}". '
            f'Possible file disguise detected.'
        )

    # Layer 5: Filename sanitization (done in upload handler)
```

> **Critical**: MIME type validation uses `python-magic` (libmagic) to inspect file magic bytes, NOT the `Content-Type` header from the client. The client header is trivially spoofable.

## Filename Sanitization

Uploaded filenames are **never used directly**. All files are renamed to prevent:

- Path traversal attacks (`../../etc/passwd`)
- Shell injection via filenames (`; rm -rf /`)
- Unicode/encoding exploits
- Filename collision across tenants

```python
# utils/filename.py

import uuid
import os
from django.utils.text import slugify

def sanitize_filename(original_name: str, organization_id: str) -> str:
    """Generate a safe, unique filename preserving the original extension."""
    ext = os.path.splitext(original_name)[1].lower()
    safe_original = slugify(os.path.splitext(original_name)[0])[:50]
    unique_id = uuid.uuid4().hex[:12]

    return f"{safe_original}_{unique_id}{ext}"
    # Example: "john-doe-resume_a1b2c3d4e5f6.pdf"
```

## Storage Isolation

### Per-Organization Bucket Structure

```
supabase-storage/
└── resumes/
    ├── org_x7y8z9w0/
    │   ├── john-doe-resume_a1b2c3d4.pdf
    │   ├── jane-smith-cv_e5f6g7h8.docx
    │   └── ...
    ├── org_m1n2o3p4/
    │   ├── candidate-a_i9j0k1l2.pdf
    │   └── ...
    └── ...
```

### Storage Access Policy

The `resumes` bucket remains private. Because product authentication uses Django-managed JWTs rather than Supabase Auth, browser clients do not receive direct Supabase Storage permissions.

Access pattern:

1. Browser uploads resume to Django.
2. Django validates file type, organization membership, and permissions.
3. Django writes to Supabase Storage using a server-side service role key.
4. Django stores the object path, not a permanent public URL.
5. Django generates signed URLs only after re-validating organization access.

The Supabase service role key must never be exposed to the frontend.

## Signed URLs for Access

Files are **never served directly**. All access goes through time-limited signed URLs:

```python
# services/storage.py

from supabase import create_client

def get_resume_url(file_path: str, expires_in: int = 3600) -> str:
    """
    Generate a signed URL for resume access.

    Args:
        file_path: Path within the resumes bucket (e.g., "org_x7y8z9/resume.pdf")
        expires_in: URL validity in seconds (default: 1 hour)

    Returns:
        Signed URL string
    """
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    result = supabase.storage.from_('resumes').create_signed_url(
        path=file_path,
        expires_in=expires_in
    )
    return result['signedURL']
```

| Parameter | Value | Rationale |
|---|---|---|
| Default expiry | 1 hour | Long enough for review session, short enough to limit exposure |
| Max expiry | 24 hours | For bulk download/export operations |
| Regeneration | On every access | Fresh URL prevents caching of expired URLs |

## Virus Scanning Considerations

| Approach | Pros | Cons | Recommended Phase |
|---|---|---|---|
| ClamAV (self-hosted) | Free, open-source, full control | Ops overhead, signature updates | Phase 2 (post-MVP) |
| AWS GuardDuty for S3 | Managed, auto-scanning | Requires S3 (not Supabase) | Future (if migrating) |
| VirusTotal API | Comprehensive scanning | Rate limits, external data sharing | Phase 2 (evaluation) |
| Quarantine pattern | Upload to staging → scan → promote | Adds upload latency | Phase 2 |

**MVP approach**: Rely on file type validation + MIME checking. Plan ClamAV integration for Phase 2 after launch.

```python
# Future: ClamAV integration sketch
import clamd

def scan_file(file_path: str) -> tuple[bool, str]:
    """Scan a file for malware using ClamAV."""
    cd = clamd.ClamdUnixSocket()
    result = cd.scan(file_path)

    if result is None:
        return (True, 'clean')

    status = result[file_path]
    if status[0] == 'OK':
        return (True, 'clean')
    else:
        return (False, status[1])  # (infected, virus_name)
```

## Upload API Response

```json
{
  "id": "file_a1b2c3d4e5f6",
  "original_name": "John_Doe_Resume.pdf",
  "stored_name": "john-doe-resume_a1b2c3d4e5f6.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 245760,
  "organization_id": "org_x7y8z9w0",
  "uploaded_by": "usr_m1n2o3p4",
  "uploaded_at": "2025-05-22T10:30:00Z",
  "status": "uploaded",
  "parsing_status": "queued"
}
```

## Related Documents

- [[resume-parser|Resume Parser]]
- [[sprint-05-resume-upload|Sprint 5 — Resume Upload & Storage]]
- [[ADR-004-supabase|ADR-004 — Supabase as Data Platform]]
- [[rate-limiting|API Rate Limiting]]
- [[resume-analysis|Resume Analysis & Data Extraction]]
