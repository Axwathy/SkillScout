---
title: "Sprint 5 — Resume Upload & Storage"
sprint_number: 5
status: planned
start_date: 2026-07-28
end_date: 2026-08-07
story_points_planned: 36
story_points_completed: 0
tags:
  - sprint
  - resume
  - upload
  - storage
---

# Sprint 5 — Resume Upload & Storage

## 🎯 Sprint Goal

> **Primary Objective:** Implement secure resume upload with storage in Supabase, comprehensive file validation, and basic text extraction to prepare resumes for downstream AI processing.
>
> **Success Criteria:** Users can upload PDF/DOCX resumes via drag-and-drop, files are validated and stored securely in Supabase Storage, and raw text is extracted and persisted for each resume.

---

## 📋 Planned Features

- [ ] Secure file upload endpoint with type and size validation
- [ ] Supabase Storage integration with signed URLs for access control
- [ ] Drag-and-drop upload UI with progress tracking
- [ ] Text extraction pipeline for PDF and DOCX formats

---

## ⚙️ Backend Tasks

- [ ] Create `Resume` model with fields: candidate, file_url, file_name, file_size, mime_type, raw_text, status, uploaded_by
- [ ] Implement `POST /api/v1/resumes/upload/` with multipart file handling
- [ ] Add file validation: allowed types (PDF, DOCX), max size (10MB), malware header check
- [ ] Integrate Supabase Storage SDK: upload to `resumes/{org_id}/{candidate_id}/` bucket path
- [ ] Generate signed download URLs with expiry for secure file access
- [ ] Implement text extraction using `pdfplumber` for PDFs and `python-docx` for DOCX files
- [ ] Create Celery task `extract_resume_text` for async text extraction after upload
- [ ] Add file deduplication check using SHA-256 hash comparison
- [ ] Write tests: upload validation, storage integration, text extraction accuracy

See also: [[resume-parser|Resume Parser]], [[upload-security|File Upload Security]]

---

## 🖥️ Frontend Tasks

- [ ] Build Resume Upload component with drag-and-drop zone using `react-dropzone`
- [ ] Implement upload progress bar with percentage and file size display
- [ ] Add file type validation on client side with user-friendly error messages
- [ ] Create file preview panel: PDF thumbnail, filename, size, upload date
- [ ] Build resume list view showing all uploaded resumes per candidate
- [ ] Add batch upload support — queue multiple files for sequential upload
- [ ] Implement delete confirmation dialog with undo grace period

---

## 🚧 Blockers & Risks

| Blocker | Impact | Mitigation | Status |
|---------|--------|------------|--------|
| Supabase Storage CORS for direct upload | Medium | Use backend proxy upload initially | 🟡 In Progress |
| Large file text extraction performance | Low | Async Celery processing with timeout | 🟢 Planned |

---

## ✅ Completed

_No items completed yet — sprint has not started._

---

## 🔧 Technical Debt

- [ ] Text extraction is basic — will be enhanced with AI parsing in [[sprint-06-resume-parsing]]
- [ ] No OCR support for scanned PDFs — future enhancement with Tesseract

---

## 📝 Sprint Notes

- **Prerequisite:** [[sprint-04-organization]] — resumes are org-scoped
- **References:** [[resume-parser|Resume Parser]], [[upload-security|File Upload Security]], [[system-overview|System Overview]]
- **Next Sprint:** [[sprint-06-resume-parsing]] — AI Resume Parsing
