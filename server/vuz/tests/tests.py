import pytest
from vuz.models import Vuz, Regions, Districts, Ministries, Training, Program

@pytest.mark.django_db
def test_vuz_view(api_client, setup_db):
    response = api_client.get("/vuz/")

    assert response.status_code == 200
    assert setup_db["vuz"].name in response.content.decode()