from typing import Union

from django.contrib.auth import mixins
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from application.models import Application
from rsvp.forms import RsvpModelForm
from rsvp.models import Rsvp
from user.models import User


class CreateRsvpView(mixins.UserPassesTestMixin, generic.CreateView):
    """
    Creates a new Rsvp and links it to a User if one doesn't already exist and the User's been accepted.
    """

    def test_func(self) -> bool:
        # Ensure user is logged-in
        user: User = self.request.user
        if not user.is_authenticated:
            return False
        app: Union[Application, None] = user.application_set.first()

        # User hasn't applied
        if not app:
            return False
        # Their application hasn't been approved (or has been rejected)
        if not app.approved:
            return False
        return True

    form_class = RsvpModelForm
    template_name = "rsvp/rsvp_form.html"
    success_url = reverse_lazy("status")

    def form_valid(self, form: RsvpModelForm):
        if Rsvp.objects.filter(user=self.request.user).exists():
            form.add_error(None, "You've already submitted an RSVP.")
            return self.form_invalid(form)
        rsvp: Rsvp = form.save(commit=False)
        rsvp.user = self.request.user
        rsvp.save()
        return redirect(self.success_url)


class UpdateRsvpView(mixins.LoginRequiredMixin, generic.UpdateView):
    """
    Updates a linked Rsvp.
    """

    success_url = reverse_lazy("status")

    def get_object(self, queryset=None) -> Rsvp:
        """
        Checks to make sure that the user actually owns the rsvp requested.
        """
        rsvp: Rsvp = super().get_object()
        if rsvp.user != self.request.user:
            raise PermissionDenied("You don't have permission to view this rsvp")
        return rsvp

    queryset = Rsvp.objects.all()
    form_class = RsvpModelForm
    template_name = "rsvp/rsvp_form.html"
