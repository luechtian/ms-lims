from django.db import models


class PartyQuerySet(models.QuerySet):
    def active(self) -> "PartyQuerySet":
        return self.filter(active=True)

    def inactive(self) -> "PartyQuerySet":
        return self.filter(active=False)
