import pytest

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
