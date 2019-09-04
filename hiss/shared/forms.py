from django.core.exceptions import ImproperlyConfigured
from django.forms import ModelForm


class PlaceholderModelForm(ModelForm):
    """
    Simply replaces the label attributes in a ModelForm with placeholders.
    """

    def __init__(self):
        super().__init__()
        if not self.placeholder_fields:
            raise ImproperlyConfigured(
                "Creating a PlaceholderModelForm without setting placeholder_fields is not allowed."
            )
        for field_name in self.base_fields:
            if field_name in self.placeholder_fields:
                if "label" in self.base_fields[field_name].widget.attrs:
                    self.base_fields[field_name].widget.attrs[
                        "placeholder"
                    ] = self.base_fields[field_name].widget.attrs["label"]
                    del self.base_fields[field_name].widget.attrs["label"]
