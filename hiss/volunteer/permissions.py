from django.contrib.auth.models import Group
from rest_framework import permissions


class IsVolunteer(permissions.BasePermission):

    """Ensures that the provided user is a volunteer by asserting that they are a member of a Group named "volunteer"."""

    group_name = "volunteer"

    def has_permission(self, request, _view):
        try:
            request.user.groups.get(name=self.group_name)
        except Group.DoesNotExist:
            return False
        else:
            return True
