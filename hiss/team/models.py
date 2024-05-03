import uuid

from django.db import models
from django.urls import reverse_lazy


class Team(models.Model):  # noqa: DJ008

    """A representation of a hackathon team that can be used for team-based admission."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # noqa: A003. As a best-practice and to avoid unforseen bugs, we really shouldn't be shadowing python builtins. But it'd be a pain to stop at this point, so just don't add more like this.
    name = models.CharField(max_length=255)
    admitted = models.NullBooleanField(blank=True)

    def get_absolute_url(self):
        return reverse_lazy("team:detail", args=[self.id])
