import uuid
from typing import TYPE_CHECKING, Self, override

from django.db import models
from django.db.models import Max, QuerySet

if TYPE_CHECKING:
    from application.models import Application


class TeamQuerySet(QuerySet):
    """Custom database queries for the Team table."""

    def order_by_latest_submission(self) -> Self:
        return self.annotate(
            latest_submission=Max("application__datetime_submitted")
        ).order_by("-latest_submission")


class Team(models.Model):
    """Represents a team in this hackathon."""

    MAX_CAPACITY: int = 4

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    captain = models.OneToOneField(
        "user.User", on_delete=models.CASCADE, related_name="captained_team"
    )
    is_active = models.BooleanField(default=True)

    objects = TeamQuerySet.as_manager()

    @override
    def __str__(self):
        return f"Team {self.id} (Captain: {self.captain.email})"

    def get_members(self) -> QuerySet["Application"]:
        return self.application_set.all()

    @property
    def is_at_max_capacity(self) -> bool:
        return self.get_members().count() >= self.MAX_CAPACITY
