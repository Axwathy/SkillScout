import time
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from apps.ai_engine.embeddings import (
    build_candidate_embedding_text,
    build_job_embedding_text,
    generate_embedding,
)
from apps.ai_engine.ranking import (
    calculate_semantic_similarity,
    extract_candidate_experience_years,
    extract_candidate_skills,
    extract_job_skills,
    extract_required_experience_years,
    score_to_percent,
)
from apps.candidates.models import ParsedResume
from apps.jobs.models import Job

SEMANTIC_WEIGHT = 0.70
KEYWORD_WEIGHT = 0.30
DEFAULT_LIMIT = 20
MAX_LIMIT = 50
MAX_SCAN_ROWS = 500
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


@dataclass(frozen=True)
class SearchFilters:
    skills: list[str]
    min_experience: float | None
    max_experience: float | None
    location: str
    remote_policy: str
    status: str
    limit: int


class SearchService:
    def __init__(self, organization):
        self.organization = organization

    def search_candidates(self, query: str, filters: SearchFilters) -> dict[str, Any]:
        started = time.perf_counter()
        query = _normalize_query(query)
        query_embedding = generate_embedding(query).vector if query else []
        query_tokens = _tokenize(query)

        queryset = (
            ParsedResume.objects.filter(
                candidate__organization=self.organization,
                status=ParsedResume.Status.COMPLETED,
            )
            .select_related("candidate", "application", "application__job")
            .order_by("-created_at")
        )[:MAX_SCAN_ROWS]

        results_by_candidate = {}
        for parsed_resume in queryset:
            candidate_skills = extract_candidate_skills(parsed_resume)
            if not _passes_skill_filter(candidate_skills, filters.skills):
                continue

            experience_years = extract_candidate_experience_years(parsed_resume)
            if not _passes_experience_filter(
                experience_years,
                filters.min_experience,
                filters.max_experience,
            ):
                continue

            location = _candidate_location(parsed_resume)
            if filters.location and filters.location.lower() not in location.lower():
                continue

            text = _candidate_search_text(parsed_resume)
            semantic_score = calculate_semantic_similarity(query_embedding, parsed_resume.embedding)
            keyword_score = _keyword_score(query_tokens, text)
            final_score = _hybrid_score(semantic_score, keyword_score)

            if query and final_score <= 0:
                continue

            candidate = parsed_resume.candidate
            application = parsed_resume.application
            result = {
                "type": "candidate",
                "id": str(candidate.id),
                "candidate_id": str(candidate.id),
                "application_id": str(application.id) if application else None,
                "job_id": str(application.job_id) if application else None,
                "resume_id": str(parsed_resume.resume_id),
                "parsed_resume_id": str(parsed_resume.id),
                "title": candidate.full_name or candidate.email,
                "subtitle": candidate.email,
                "location": location,
                "url": f"/dashboard/candidates/{candidate.id}",
                "score": score_to_percent(final_score),
                "score_normalized": final_score,
                "semantic_score": score_to_percent(semantic_score),
                "keyword_score": score_to_percent(keyword_score),
                "matched_terms": _matched_terms(query_tokens, text),
                "matched_skills": _matched_skills(candidate_skills, filters.skills),
                "skills": candidate_skills[:12],
                "experience_years": experience_years,
                "explanation": _candidate_explanation(
                    semantic_score,
                    keyword_score,
                    candidate_skills,
                    filters.skills,
                    experience_years,
                ),
                "_created_at": parsed_resume.created_at,
            }
            current = results_by_candidate.get(candidate.id)
            if current is None or _is_better_candidate_result(result, current):
                results_by_candidate[candidate.id] = result

        results = list(results_by_candidate.values())
        for result in results:
            result.pop("_created_at", None)
        results = sorted(
            results,
            key=lambda item: (item["score_normalized"], item["keyword_score"], item["title"]),
            reverse=True,
        )[: filters.limit]
        return _response(query, filters, started, results)

    def search_jobs(self, query: str, filters: SearchFilters) -> dict[str, Any]:
        started = time.perf_counter()
        query = _normalize_query(query)
        query_embedding = generate_embedding(query).vector if query else []
        query_tokens = _tokenize(query)

        queryset = Job.objects.filter(organization=self.organization).order_by("-created_at")
        if filters.status:
            queryset = queryset.filter(status=filters.status)
        if filters.remote_policy:
            queryset = queryset.filter(remote_policy=filters.remote_policy)
        if filters.location:
            queryset = queryset.filter(location__icontains=filters.location)

        results = []
        for job in queryset[:MAX_SCAN_ROWS]:
            job_skills = extract_job_skills(job)
            if not _passes_skill_filter(job_skills, filters.skills):
                continue

            required_years = extract_required_experience_years(job)
            if not _passes_experience_filter(
                required_years,
                filters.min_experience,
                filters.max_experience,
            ):
                continue

            text = build_job_embedding_text(job)
            semantic_score = calculate_semantic_similarity(query_embedding, job.embedding)
            keyword_score = _keyword_score(query_tokens, text)
            final_score = _hybrid_score(semantic_score, keyword_score)

            if query and final_score <= 0:
                continue

            results.append(
                {
                    "type": "job",
                    "id": str(job.id),
                    "job_id": str(job.id),
                    "title": job.title,
                    "subtitle": f"{job.get_employment_type_display()} - {job.location}",
                    "location": job.location,
                    "remote_policy": job.remote_policy,
                    "status": job.status,
                    "url": f"/dashboard/jobs/{job.id}",
                    "score": score_to_percent(final_score),
                    "score_normalized": final_score,
                    "semantic_score": score_to_percent(semantic_score),
                    "keyword_score": score_to_percent(keyword_score),
                    "matched_terms": _matched_terms(query_tokens, text),
                    "matched_skills": _matched_skills(job_skills, filters.skills),
                    "skills": job_skills[:12],
                    "required_experience_years": required_years,
                    "explanation": _job_explanation(
                        semantic_score,
                        keyword_score,
                        job_skills,
                        filters.skills,
                        required_years,
                    ),
                }
            )

        results = sorted(
            results,
            key=lambda item: (item["score_normalized"], item["keyword_score"], item["title"]),
            reverse=True,
        )[: filters.limit]
        return _response(query, filters, started, results)

    def search_all(self, query: str, filters: SearchFilters) -> dict[str, Any]:
        started = time.perf_counter()
        candidate_response = self.search_candidates(query, filters)
        job_response = self.search_jobs(query, filters)
        results = sorted(
            [*candidate_response["results"], *job_response["results"]],
            key=lambda item: (item["score_normalized"], item["keyword_score"], item["title"]),
            reverse=True,
        )[: filters.limit]
        return _response(query, filters, started, results)


def build_search_filters(params) -> SearchFilters:
    return SearchFilters(
        skills=_split_csv(params.get("skills", "")),
        min_experience=_float_or_none(params.get("min_experience")),
        max_experience=_float_or_none(params.get("max_experience")),
        location=(params.get("location") or "").strip(),
        remote_policy=(params.get("remote_policy") or "").strip(),
        status=(params.get("status") or "").strip(),
        limit=_limit_or_default(params.get("limit")),
    )


def _response(
    query: str,
    filters: SearchFilters,
    started: float,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "query": query,
        "count": len(results),
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        "weights": {
            "semantic": SEMANTIC_WEIGHT,
            "keyword": KEYWORD_WEIGHT,
        },
        "filters": {
            "skills": filters.skills,
            "min_experience": filters.min_experience,
            "max_experience": filters.max_experience,
            "location": filters.location,
            "remote_policy": filters.remote_policy,
            "status": filters.status,
            "limit": filters.limit,
        },
        "results": results,
    }


def _candidate_search_text(parsed_resume: ParsedResume) -> str:
    candidate = parsed_resume.candidate
    values = [
        candidate.full_name,
        candidate.email,
        candidate.phone,
        _candidate_location(parsed_resume),
        build_candidate_embedding_text(parsed_resume),
    ]
    return " ".join(value for value in values if value)


def _candidate_location(parsed_resume: ParsedResume) -> str:
    personal_info = (parsed_resume.data or {}).get("personal_info") or {}
    return str(personal_info.get("location") or "")


def _hybrid_score(semantic_score: float, keyword_score: float) -> float:
    return round((SEMANTIC_WEIGHT * semantic_score) + (KEYWORD_WEIGHT * keyword_score), 5)


def _keyword_score(query_tokens: list[str], text: str) -> float:
    if not query_tokens:
        return 0.0
    matches = _matched_terms(query_tokens, text)
    if not matches:
        return 0.0
    matches = list(dict.fromkeys(matches))
    return round(len(matches) / len(query_tokens), 5)


def _matched_terms(query_tokens: list[str], text: str) -> list[str]:
    text_terms = _text_term_index(text)
    return [token for token in query_tokens if _term_matches(token, text_terms)]


def _passes_skill_filter(source_skills: list[str], required_skills: list[str]) -> bool:
    if not required_skills:
        return True
    normalized_source = {_normalize_skill(skill) for skill in source_skills}
    return all(_normalize_skill(skill) in normalized_source for skill in required_skills)


def _matched_skills(source_skills: list[str], required_skills: list[str]) -> list[str]:
    if not required_skills:
        return []
    normalized_required = {_normalize_skill(skill) for skill in required_skills}
    return [skill for skill in source_skills if _normalize_skill(skill) in normalized_required]


def _passes_experience_filter(
    years: float | None,
    min_experience: float | None,
    max_experience: float | None,
) -> bool:
    if min_experience is not None and (years is None or years < min_experience):
        return False
    if max_experience is not None and years is not None and years > max_experience:
        return False
    return True


def _candidate_explanation(
    semantic_score: float,
    keyword_score: float,
    candidate_skills: list[str],
    filter_skills: list[str],
    experience_years: float | None,
) -> str:
    parts = [
        f"Semantic relevance {score_to_percent(semantic_score)}",
        f"keyword match {score_to_percent(keyword_score)}",
    ]
    matched = _matched_skills(candidate_skills, filter_skills)
    if matched:
        parts.append(f"matched skills: {', '.join(matched)}")
    if experience_years is not None:
        parts.append(f"{experience_years:g} years experience")
    return "; ".join(parts) + "."


def _job_explanation(
    semantic_score: float,
    keyword_score: float,
    job_skills: list[str],
    filter_skills: list[str],
    required_years: float | None,
) -> str:
    parts = [
        f"Semantic relevance {score_to_percent(semantic_score)}",
        f"keyword match {score_to_percent(keyword_score)}",
    ]
    matched = _matched_skills(job_skills, filter_skills)
    if matched:
        parts.append(f"required skills: {', '.join(matched)}")
    if required_years is not None:
        parts.append(f"requires {required_years:g}+ years")
    return "; ".join(parts) + "."


def _normalize_query(query: str) -> str:
    return " ".join((query or "").split())


def _tokenize(text: str) -> list[str]:
    return [
        token
        for token in (_normalize_token(raw_token) for raw_token in _split_terms(text))
        if token and token not in STOPWORDS
    ]


def _text_term_index(text: str) -> dict[str, set[str] | str]:
    tokens = set(_tokenize(text))
    normalized = {_compact_token(token) for token in tokens if _compact_token(token)}
    compact_text = _compact_token(text)
    return {
        "tokens": tokens,
        "normalized": normalized,
        "compact_text": compact_text,
    }


def _term_matches(token: str, text_terms: dict[str, set[str] | str]) -> bool:
    tokens = text_terms["tokens"]
    normalized = text_terms["normalized"]
    compact_text = text_terms["compact_text"]
    if not isinstance(tokens, set) or not isinstance(normalized, set):
        return False
    if not isinstance(compact_text, str):
        return False

    variants = _token_variants(token)
    if variants & tokens:
        return True

    compact_variants = {_compact_token(variant) for variant in variants}
    compact_variants.discard("")
    if compact_variants & normalized:
        return True

    return any(len(variant) >= 3 and variant in compact_text for variant in compact_variants)


def _token_variants(token: str) -> set[str]:
    token = _normalize_token(token)
    compact = _compact_token(token)
    variants = {token, compact}
    if compact.endswith("s") and len(compact) > 3:
        variants.add(compact[:-1])
    return {variant for variant in variants if variant}


def _split_terms(text: str) -> Iterable[str]:
    value = []
    current = []
    for char in text or "":
        if char.isalnum() or char in {"+", "#", "."}:
            current.append(char)
        elif current:
            value.append("".join(current))
            current = []
    if current:
        value.append("".join(current))
    return value


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def _normalize_skill(skill: str) -> str:
    return "".join(char.lower() for char in skill if char.isalnum() or char in {"+", "#", "."})


def _normalize_token(token: str) -> str:
    return (token or "").strip().lower()


def _compact_token(token: str) -> str:
    return "".join(char.lower() for char in token or "" if char.isalnum() or char in {"+", "#"})


def _is_better_candidate_result(
    result: dict[str, Any],
    current: dict[str, Any],
) -> bool:
    result_rank = (
        result["score_normalized"],
        result["keyword_score"],
        result["_created_at"],
    )
    current_rank = (
        current["score_normalized"],
        current["keyword_score"],
        current["_created_at"],
    )
    return result_rank > current_rank


def _float_or_none(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _limit_or_default(value: Any) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    return min(max(limit, 1), MAX_LIMIT)
