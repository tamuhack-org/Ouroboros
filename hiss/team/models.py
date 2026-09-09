import uuid
from typing import TYPE_CHECKING, Self, override

from django.db import IntegrityError, models, router, transaction
from django.db.models import Max, QuerySet

from hiss.settings.customization import MAX_TEAM_CAPACITY
from team.codes import generate_team_code

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
    code = models.CharField(max_length=64, default=generate_team_code, editable=False)

    is_active = models.BooleanField(default=True)

    objects = TeamQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_active=True),
                name="unique_active_team_code",
            )
        ]

    @override
    def __str__(self):
        if self.captain:
            return f"Team {self.id} (Captain: {self.captain.user.email})"
        return f"Team {self.id} (No Captain)"

    @override
    def save(self, *args, **kwargs):
        if not self._state.adding:
            super().save(*args, **kwargs)
            return

        using = kwargs.get("using") or router.db_for_write(type(self), instance=self)
        for remaining in reversed(range(10)):
            try:
                # A savepoint allows retrying a collision inside an outer transaction.
                with transaction.atomic(using=using):
                    super().save(*args, **kwargs)
            except IntegrityError:
                if (
                    not remaining
                    or not type(self)
                    .objects.using(using)
                    .filter(code=self.code, is_active=True)
                    .exists()
                ):
                    raise
                self.code = generate_team_code()
            else:
                return

    def get_members(self) -> QuerySet["Application"]:
        return self.members.all()

    @property
    def captain(self) -> "Application | None":
        return self.members.filter(is_captain=True).first()

    @property
    def is_at_max_capacity(self) -> bool:
        return self.get_members().count() >= MAX_TEAM_CAPACITY
