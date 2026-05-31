import json

import pytest
from django.conf import settings
from django.core.management import call_command

from parties.models import Person, ResearchGroup


def test_internal_lab_fixture_is_valid_json():
    path = settings.BASE_DIR / "parties" / "fixtures" / "internal_lab.json"

    with open(path) as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.django_db
def test_loaddata_creates_internal_lab():
    call_command("loaddata", "internal_lab", app_label="parties")

    group = ResearchGroup.objects.get(name="Internes Lab")

    assert group.persons.count() >= 1
    assert group.pi_id is not None


@pytest.mark.django_db
def test_loaddata_is_idempotent():
    call_command("loaddata", "internal_lab", app_label="parties")

    n_groups1 = ResearchGroup.objects.count()
    n_persons1 = Person.objects.count()

    call_command("loaddata", "internal_lab", app_label="parties")

    n_groups2 = ResearchGroup.objects.count()
    n_persons2 = Person.objects.count()

    assert n_groups1 == n_groups2
    assert n_persons1 == n_persons2


@pytest.mark.django_db(transaction=True)
def test_migrate_seeds_internal_lab():
    assert ResearchGroup.objects.filter(name="Internes Lab").exists()
