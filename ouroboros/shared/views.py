from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView


class CreateUpdateView(
    SingleObjectTemplateResponseMixin, ModelFormMixin, ProcessFormView
):
    """
    If the instance requested by the user does not exist, the user is
    redirected to a CreateView, otherwise they're redirected to a view
    containing their instance for updating.
    """

    def get_object(self, queryset=None):
        try:
            return super(CreateUpdateView, self).get_object(queryset)
        except AttributeError:
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(CreateUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(CreateUpdateView, self).post(request, *args, **kwargs)
