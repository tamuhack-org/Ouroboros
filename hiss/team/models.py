import uuid

from django.db import models
from django.urls import reverse_lazy


class Team(models.Model):
    """A representation of a hackathon team that can be used for team-based admission."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    admitted = models.NullBooleanField(blank=True)

    def get_absolute_url(self):
        return reverse_lazy("team:detail", args=[self.id])
