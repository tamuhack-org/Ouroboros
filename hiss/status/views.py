from django.contrib.auth import mixins
from django.views import generic

from application import models as application_models
from application.models import Wave, Application
from user.models import User


class StatusView(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "status/status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user: User = self.request.user

        active_wave = Wave.objects.active_wave()
        if not active_wave and not user.application_set.exists():
            next_wave = Wave.objects.next_wave()
            if not next_wave:
                context["NO_MORE_WAVES"] = True
            else:
                context["WAIT_UNTIL_NEXT_WAVE"] = True
                context["next_wave_start"] = next_wave.start
        else:
            if active_wave:
                context["active_wave_end"] = active_wave.end
            if not user.application_set.exists():
                context["NOT_APPLIED"] = True
                return context
            app: Application = user.application_set.first()
            app_status = app.status
            if app_status == application_models.STATUS_PENDING:
                context["PENDING"] = True
                context["application"] = app
            elif app_status == application_models.STATUS_REJECTED:
                context["REJECTED"] = True
            elif app_status == application_models.STATUS_ADMITTED:
                context["NEEDS_TO_CONFIRM"] = True
                context["application"] = app
                context["confirmation_deadline"] = app.confirmation_deadline
            elif app_status == application_models.STATUS_CONFIRMED:
                context["CONFIRMED"] = True
            elif app_status == application_models.STATUS_DECLINED:
                context["DECLINED"] = True
            elif app_status == application_models.STATUS_CHECKED_IN:
                context["CHECKED_IN"] = True
            elif app_status == application_models.STATUS_EXPIRED:
                context["EXPIRED"] = True
        return context
