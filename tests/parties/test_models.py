import pytest
from django.core.exceptions import ValidationError

from tests.parties.factories import (
    InstitutionFactory,
    PersonFactory,
    ResearchGroupFactory,
)


@pytest.mark.django_db
def test_foundation_can_create_all_three():
    institution = InstitutionFactory()
    group = ResearchGroupFactory(institution=institution)
    person = PersonFactory(research_group=group)

    assert institution.pk is not None
    assert group.pk is not None
    assert person.pk is not None


@pytest.mark.django_db
def test_pi_can_be_none_on_new_group():
    group = ResearchGroupFactory(pi=None)
    assert group.pi is None


@pytest.mark.django_db
def test_pi_must_be_member_happy_path():
    group = ResearchGroupFactory(pi=None)
    person = PersonFactory(research_group=group)

    group.pi = person

    group.full_clean()
    group.save()

    assert group.pi == person


@pytest.mark.django_db
def test_pi_must_be_member_rejects_other_group():
    group1 = ResearchGroupFactory(pi=None)
    group2 = ResearchGroupFactory(pi=None)

    person = PersonFactory(research_group=group2)

    group1.pi = person

    with pytest.raises(ValidationError) as exc_info:
        group1.full_clean()

    assert "pi" in exc_info.value.message_dict
