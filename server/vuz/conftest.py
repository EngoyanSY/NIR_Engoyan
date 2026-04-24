import pytest
from vuz.models import Vuz, Regions, Districts, Ministries, Training, Program

@pytest.fixture
def api_client():
    from django.test import Client
    return Client()

@pytest.fixture
def setup_db(db):
    district = Districts.objects.create(id_district=1, district="Ценнтральный")
    region = Regions.objects.create(id_region=1, region="г. Москва", id_district=district)
    ministry = Ministries.objects.create(id_ministry=1, ministry="Министерство образования")

    vuz = Vuz.objects.create(
        id_listedu=1,
        id_parent=1,
        name = "МГУ",
        id_region = region,
        id_district = district,
        id_ministry = ministry,
    )

    program = Program.objects.create(
        progid = "62",
        progname = "Бакалавриат",
        progcode = 3,
    )

    training = Training.objects.create(
        fieldid = "11.03.01",
        fieldname = "Радиотехника",
        progid = program,
    )

    return {
        "regions" : region,
        "districts" : district,
        "regions" : region,
        "ministry" : ministry,
        "vuz" : vuz,
    }