from django import views
from django.contrib.auth import login
from django.contrib.sites import shortcuts as site_shortcuts
from django.core import mail as django_email
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import generic

from confirm import forms as confirm_forms
from confirm.tokens import email_confirmation_generator
from django.contrib.auth import get_user_model

# Create your views here.
class SignupView(generic.FormView):
    form_class = confirm_forms.SignupForm
    template_name = "registration/signup.html"

    def form_valid(self, form):
        user: hacker_models.Hacker = form.save(commit=False)
        user.is_active = False
        user.save()
        curr_domain = site_shortcuts.get_current_site(self.request)
        subject = "Confirm your email address!"
        msg = render_to_string(
            "emails/activate_email.html",
            {
                "user": user,
                "domain": curr_domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": email_confirmation_generator.make_token(user),
            },
        )
        to_email = form.cleaned_data.get("email")
        email = django_email.EmailMessage(subject, msg, to=[to_email])
        email.send()
        return HttpResponse(
            "Please confirm your email address to complete your registration!"
        )


class ActivateView(views.View):
    def get(self, request, *args, **kwargs):
        hacker = None
        try:
            uid = force_text(urlsafe_base64_decode(kwargs["uidb64"]))
            hacker = get_user_model().objects.get(id=int(uid))
        except (
            TypeError,
            ValueError,
            OverflowError,
            get_user_model().DoesNotExist,
        ) as e:
            print(e)
        if hacker is not None and email_confirmation_generator.check_token(
            hacker, kwargs["token"]
        ):
            hacker.is_active = True
            hacker.save()
            login(request, hacker)
            return redirect(reverse_lazy("status"))
        else:
            return HttpResponse("Activation link is invalid.")
