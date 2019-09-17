from django.views import generic


class StatusView(generic.TemplateView):
    template_name = "status/status.html"
