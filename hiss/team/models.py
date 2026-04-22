import uuid
from typing import TYPE_CHECKING, Self, override

from django.db import models
from django.db.models import Max, QuerySet

from hiss.settings.customization import MAX_TEAM_CAPACITY

if TYPE_CHECKING:
    from application.models import Application


class TeamQuerySet(QuerySet):
    """Custom database queries for the Team table."""

    def order_by_latest_submission(self) -> Self:
        return self.annotate(
            latest_submission=Max("members__datetime_submitted")
        ).order_by("-latest_submission")


class Team(models.Model):
    """Represents a team in this hackathon."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    is_active = models.BooleanField(default=True)

    objects = TeamQuerySet.as_manager()

    @override
    def __str__(self):
        return f"Team {self.id} (Captain: {self.captain.user.email})"

    def get_members(self) -> QuerySet["Application"]:
        return self.members.all()

    @property
    def captain(self) -> "Application | None":
        return self.members.filter(is_captain=True).first()

    @property
    def is_at_max_capacity(self) -> bool:
        return self.get_members().count() >= MAX_TEAM_CAPACITY
