
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsVerifiedRecruiter
from apps.candidates.views import get_recruiter_organization
from apps.core.cache import org_cache_key

from .search import SearchService, build_search_filters


class SearchBaseView(APIView):
    permission_classes = [IsVerifiedRecruiter]
    throttle_scope = "search"
    search_type = "all"

    def get(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        query = request.query_params.get("q", "")
        filters = build_search_filters(request.query_params)
        cache_key = self._cache_key(organization.id, request.query_params.urlencode())
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        service = SearchService(organization)
        if self.search_type == "candidates":
            payload = service.search_candidates(query, filters)
        elif self.search_type == "jobs":
            payload = service.search_jobs(query, filters)
        else:
            payload = service.search_all(query, filters)

        payload["type"] = self.search_type
        cache.set(cache_key, payload, timeout=60)
        return Response(payload)

    def _cache_key(self, organization_id, encoded_params: str) -> str:
        return org_cache_key("search", organization_id, self.search_type, encoded_params)


class SearchAllView(SearchBaseView):
    search_type = "all"


class CandidateSearchView(SearchBaseView):
    search_type = "candidates"


class JobSearchView(SearchBaseView):
    search_type = "jobs"
