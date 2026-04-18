import factory
from factory.django import DjangoModelFactory

from parties.models import Institution, Person, ResearchGroup


class InstitutionFactory(DjangoModelFactory):
    class Meta:
        model = Institution

    name = factory.Sequence(lambda n: f"Institution {n}")
    active = True


class ResearchGroupFactory(DjangoModelFactory):
    class Meta:
        model = ResearchGroup

    name = factory.Sequence(lambda n: f"ResearchGroup {n}")
    institution = None
    pi = None
    active = True


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence(lambda n: f"person{n}@example.com")
    research_group = factory.SubFactory(ResearchGroupFactory)
    active = True
