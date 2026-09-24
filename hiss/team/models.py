import uuid
from typing import TYPE_CHECKING, Self, override

from django.db import IntegrityError, models, router, transaction
from django.db.models import Count, F, Max, Q, QuerySet

from application.constants import (
    STATUS_ADMITTED,
    STATUS_CHECKED_IN,
    STATUS_CONFIRMED,
    STATUS_DECLINED,
    STATUS_EXPIRED,
    STATUS_PENDING,
    STATUS_REJECTED,
)
from hiss.settings.customization import MAX_TEAM_CAPACITY
from team.codes import generate_team_code

if TYPE_CHECKING:
    from application.models import Application


class TeamStatus(models.TextChoices):
    ACCEPTED = ("accepted", "Accepted")
    REJECTED = ("rejected", "Rejected")
    IN_REVIEW = ("in_review", "In review")
    MIXED = ("mixed", "Mixed")


class TeamQuerySet(QuerySet):
    """Custom database queries for the Team table."""

    def order_by_latest_submission(self) -> Self:
        return self.annotate(
            latest_submission=Max("members__datetime_submitted")
        ).order_by("-latest_submission")

    def with_team_status(self) -> Self:
        """Annotate each team with its status based on its members' statuses."""
        accepted = [STATUS_ADMITTED, STATUS_CONFIRMED, STATUS_CHECKED_IN]
        rejected = [STATUS_REJECTED, STATUS_DECLINED]
        in_review = [STATUS_PENDING, STATUS_EXPIRED]

        return self.annotate(
            member_count=Count("members"),
            accepted_count=Count("members", filter=Q(members__status__in=accepted)),
            rejected_count=Count("members", filter=Q(members__status__in=rejected)),
            in_review_count=Count("members", filter=Q(members__status__in=in_review)),
        ).annotate(
            computed_team_status=models.Case(
                models.When(
                    member_count=0,
                    then=models.Value(TeamStatus.IN_REVIEW),
                ),
                models.When(
                    accepted_count=F("member_count"),
                    then=models.Value(TeamStatus.ACCEPTED),
                ),
                models.When(
                    rejected_count=F("member_count"),
                    then=models.Value(TeamStatus.REJECTED),
                ),
                models.When(
                    in_review_count=F("member_count"),
                    then=models.Value(TeamStatus.IN_REVIEW),
                ),
                default=models.Value(TeamStatus.MIXED),
                output_field=models.CharField(),
            )
        )


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
