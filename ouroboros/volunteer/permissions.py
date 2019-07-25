from django.conf import settings
from django.contrib.auth.models import Group
from rest_framework import exceptions, permissions


class IsVolunteer(permissions.BasePermission):
    group_name = settings.VOLUNTEER_GROUP_NAME

    def has_permission(self, request, view):
        try:
            request.user.groups.get(name=self.group_name)
            return True
        except Group.DoesNotExist:
            return False
