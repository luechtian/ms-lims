import pytest

from parties.models import Institution, Person, ResearchGroup
from tests.parties.factories import (
    InstitutionFactory,
    PersonFactory,
    ResearchGroupFactory,
)


@pytest.mark.django_db
def test_party_queryset_active_filters_inactive():
    active_inst = InstitutionFactory()
    active_group = ResearchGroupFactory()
    active_person = PersonFactory()

    inactive_inst = InstitutionFactory(active=False)
    inactive_group = ResearchGroupFactory(active=False)
    inactive_person = PersonFactory(active=False)

    qs_inst = Institution.objects.active()
    qs_group = ResearchGroup.objects.active()
    qs_person = Person.objects.active()

    assert active_inst in qs_inst
    assert inactive_inst not in qs_inst
    assert active_group in qs_group
    assert inactive_group not in qs_group
    assert active_person in qs_person
    assert inactive_person not in qs_person


@pytest.mark.django_db
def test_party_queryset_inactive_is_complement():
    InstitutionFactory.create_batch(2)
    ResearchGroupFactory.create_batch(2)
    PersonFactory.create_batch(2)

    InstitutionFactory.create_batch(1, active=False)
    ResearchGroupFactory.create_batch(1, active=False)
    PersonFactory.create_batch(1, active=False)

    n_active_inst = Institution.objects.active().count()
    n_active_groups = ResearchGroup.objects.active().count()
    n_active_persons = Person.objects.active().count()

    n_inactive_inst = Institution.objects.inactive().count()
    n_inactive_groups = ResearchGroup.objects.inactive().count()
    n_inactive_persons = Person.objects.inactive().count()

    assert n_active_inst + n_inactive_inst == Institution.objects.count()
    assert n_active_groups + n_inactive_groups == ResearchGroup.objects.count()
    assert n_active_persons + n_inactive_persons == Person.objects.count()
