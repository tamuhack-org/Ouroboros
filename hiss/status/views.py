from django.contrib.auth import mixins
from django.utils import timezone
from django.views import generic

from application.models import Wave
from user.models import User


class StatusView(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = "status/status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user: User = self.request.user

        active_wave = Wave.objects.active_wave(start_dt=timezone.now())
        # TODO: Add hacker can't make it context
        if not active_wave and not user.application_set.exists():
            next_wave = Wave.objects.next_wave(start_dt=timezone.now())
            if not next_wave:
                context["NO_MORE_WAVES"] = True
            else:
                context["WAIT_UNTIL_NEXT_WAVE"] = True
                context["next_wave_start"] = next_wave.start
        else:
            if not user.application_set.exists():
                context["active_wave_end"] = active_wave.end
                context["NEEDS_TO_APPLY"] = True
            elif user.application_set.first().approved is None:
                context["application"] = user.application_set.first()
                context["PENDING"] = True
            else:
                if user.application_set.first().approved:
                    if not user.rsvp_set.exists():
                        # TODO: Add context if user didn't RSVP in time
                        if user.rsvp_deadline < timezone.now():
                            context["RSVP_DEADLINE_EXPIRED"] = True
                        else:
                            context["rsvp_deadline"] = user.rsvp_deadline
                            context["NEEDS_TO_RSVP"] = True
                    else:
                        context["CONFIRMED"] = True
                else:
                    context["REJECTED"] = True
        return context
