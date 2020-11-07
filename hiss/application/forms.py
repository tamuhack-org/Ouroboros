import ast

from django import forms
from django.utils.safestring import mark_safe

from application import models as application_models
from application.models import School

from address.forms import AddressField


class ApplicationModelForm(forms.ModelForm):

    required_css_class = "required-form-input"

    gender_other = forms.CharField(
        label='If you chose "Prefer to self-describe", please elaborate.',
        required=False,
    )
    race_other = forms.CharField(
        label='If you chose "Prefer to self-describe", please elaborate.',
        required=False,
    )
    school = forms.ModelChoiceField(
        School.objects.all(),
        label="What school do you go to?",
    )
    school_other = forms.CharField(
        label='If you chose "Other", please enter your school\'s name here.',
        required=False,
    )

    # Languages
    PYTHON = "Python"
    JAVA_SCRIPT = "JavaScript"
    TYPE_SCRIPT = "TypeScript"
    JAVA = "Java"
    C_SHARP = "C#"
    C_LANG = "C"
    CPP = "C++"
    GOLANG = "Go"
    R_LANG = "R"
    SWIFT = "Swift"
    DART = "Dart"
    KOTLIN = "Kotlin"
    RUBY = "Ruby"
    RUST = "Rust"
    SCALA = "Scala"
    # Concepts
    MACHINE_LEARNING = "ML"
    FULL_STACK = "full-stack"
    FRONT_END = "front-end"
    BACK_END = "back-end"
    WEB = "web-dev"
    MOBILE = "mobile-dev"
    DESIGN = "design"
    DATA_SCIENCE = "data-science"
    DEV_OPS = "dev-ops"
    CLOUD = "cloud"

    TECHNOLOGY_EXPERIENCE = (
        (PYTHON, "Python"),
        (JAVA_SCRIPT, "JavaScript"),
        (TYPE_SCRIPT, "TypeScript"),
        (JAVA, "Java"),
        (C_SHARP, "C#"),
        (C_LANG, "C"),
        (CPP, "C++"),
        (GOLANG, "Golang"),
        (R_LANG, "R"),
        (SWIFT, "Swift"),
        (DART, "Dart"),
        (KOTLIN, "Kotlin"),
        (RUBY, "Ruby"),
        (RUST, "Rust"),
        (SCALA, "Scala"),
        (FULL_STACK, "Full Stack"),
        (FRONT_END, "Front End"),
        (BACK_END, "Back End"),
        (WEB, "Web"),
        (MOBILE, "Mobile"),
        (DESIGN, "Design"),
        (DEV_OPS, "Dev Ops"),
        (CLOUD, "Cloud (AWS, etc.)"),
        (DATA_SCIENCE, "Data Science"),
        (MACHINE_LEARNING, "Machine Learning"),
    )
    # SKILLS
    technology_experience = forms.MultipleChoiceField(
        label="What technical skills do you have?",
        help_text="Select all that apply",
        choices=TECHNOLOGY_EXPERIENCE,
        required=False,
    )
    
    address = AddressField(help_text="We will use your address for swag and prizes",required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get("instance"):
            kwargs["initial"] = {
                "technology_experience": ast.literal_eval(
                    kwargs.get("instance").technology_experience or "[]"
                ),
            }

        super().__init__(*args, **kwargs)
        self.fields["agree_to_coc"].label = mark_safe(
            'I agree to the <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf">MLH Code of Conduct</a>'
        )

        # HACK: Disable the form if there's not an active wave
        if not application_models.Wave.objects.active_wave():
            for field_name in self.fields.keys():
                self.fields[field_name].widget.attrs["disabled"] = "disabled"

    def is_valid(self) -> bool:
        """
        Checks to ensure that a wave is currently active.
        """
        if not application_models.Wave.objects.active_wave():
            self.add_error(
                None,
                "Applications may only be submitted during an active registration wave.",
            )
        return super().is_valid()

    def clean(self):
        gender = self.cleaned_data.get("gender")
        if gender == application_models.GENDER_OTHER:
            gender_other = self.cleaned_data.get("gender_other")
            if not gender_other:
                msg = forms.ValidationError(
                    'Please fill out this field or choose "Prefer not to answer".'
                )
                self.add_error("gender_other", msg)
        races = self.cleaned_data.get("race")
        if races:
            race_other = self.cleaned_data.get("race_other")
            if application_models.RACE_OTHER in races and not race_other:
                msg = forms.ValidationError(
                    "Please fill out this field with the appropriate information."
                )
                self.add_error("race_other", msg)
        return self.cleaned_data

    class Meta:
        model = application_models.Application
        widgets = {
            "is_adult": forms.CheckboxInput,
            "agree_to_coc": forms.CheckboxInput,
            "travel_reimbursement": forms.CheckboxInput,
            "extra_links": forms.TextInput(
                attrs={
                    "placeholder": "ex. GitHub, Devpost, personal website, LinkedIn, etc."
                }
            ),
        }

        fields = [
            "first_name",
            "last_name",
            "school",
            "school_other",
            "major",
            "classification",
            "grad_year",
            "gender",
            "gender_other",
            "race",
            "race_other",
            "num_hackathons_attended",
            "technology_experience",
            "has_team",
            "wants_team",
            "shirt_size",
            "address",
            "resume",
            "extra_links",
            "question1",
            "question2",
            "question3",
            "additional_accommodations",
            "notes",
            "agree_to_coc",
            "is_adult",
        ]
