import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health_check_returns_service_and_database_status(client):
    response = client.get(reverse("core:health"))

    assert response.status_code == 200
    assert response.json() == {
        "service": "ai-recruitment-api",
        "status": "ok",
        "database": "ok",
    }

