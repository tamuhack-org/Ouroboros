from django import views
from django.views import generic


class DashboardView(views.View):
    pass


class ApplicationView(generic.FormView):
    pass


class StatusView(views.View):
    pass


class RsvpView(generic.FormView):
    pass
