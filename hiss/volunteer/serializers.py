from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class EmailAuthTokenSerializer(serializers.Serializer):
    """
    This class is essentially a clone of the `AuthTokenSerializer` class implemented by Django Rest Framework,
    but instead of looking for "username", it looks for "email" (see
    https://github.com/encode/django-rest-framework/blob/8988afa0827a139efeeb72afb21da08670fb4775/rest_framework
    /authtoken/serializers.py#L7 for more context)
    """

    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            # The authenticate call simply returns None for is_active=False
            # users.
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")
        attrs["user"] = user
        return attrs
