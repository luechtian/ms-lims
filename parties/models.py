from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from parties.managers import PartyQuerySet


class Institution(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, default="")
    website = models.URLField(blank=True, default="")
    active = models.BooleanField(default=True, db_index=True)

    objects = PartyQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(Lower("name"), name="uniq_institution_name_ci"),
        ]

    def __str__(self):
        return self.name


class ResearchGroup(models.Model):
    name = models.CharField(max_length=255)
    institution = models.ForeignKey(
        Institution,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="research_groups",
    )
    pi = models.ForeignKey(
        "Person",  # not defined yet
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PartyQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "institution",
                name="uniq_group_name_in_institution_ci",
                condition=Q(institution__isnull=False),
            ),
            models.UniqueConstraint(
                Lower("name"),
                name="uniq_group_name_no_institution_ci",
                condition=Q(institution__isnull=True),
            ),
        ]

    def __str__(self):
        return self.name

    def active_members(self):
        return self.persons.active()


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    research_group = models.ForeignKey(
        ResearchGroup, on_delete=models.PROTECT, related_name="persons"
    )
    active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PartyQuerySet.as_manager()

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
