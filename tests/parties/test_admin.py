from parties.models import Institution, Person, ResearchGroup


def test_admin_onboarding_flow_roundtrip(admin_client):
    response = admin_client.post(
        "/admin/parties/institution/add/",
        {
            "name": "Uni Munich",
            "active": True,
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    institution = Institution.objects.get(name="Uni Munich")

    response = admin_client.post(
        "/admin/parties/researchgroup/add/",
        {
            "name": "AG Mueller",
            "institution": institution.pk,
            "active": True,
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    group = ResearchGroup.objects.get(name="AG Mueller")

    response = admin_client.post(
        "/admin/parties/person/add/",
        {
            "first_name": "Alice",
            "last_name": "Mueller",
            "email": "alice@example.com",
            "research_group": group.pk,
            "active": True,
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    person = Person.objects.get(email="alice@example.com")

    response = admin_client.post(
        f"/admin/parties/researchgroup/{group.pk}/change/",
        {
            "name": "AG Mueller",
            "institution": institution.pk,
            "pi": person.pk,
            "active": True,
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    group.refresh_from_db()
    assert group.pi == person
