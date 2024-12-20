import ast
import json

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.db.models import Case, When, IntegerField

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
    major_other = forms.CharField(
        label='If you chose "Other", please specify your major.',
        required=False,
    )

    # 1565 is the ID for Texas A&M University
    school = forms.ModelChoiceField(
        queryset=School.objects.annotate(
            priority=Case(
                When(pk=1565, then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by('priority', 'id'),
        label="What school do you go to?"
    )

    school_other = forms.CharField(
        label='If you chose "Other", please enter your school\'s name here.',
        required=False,
    )
    tamu_email = forms.CharField(
        label="TAMU Email if you are a Texas A&M student",
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
    SQL = "SQL"
    HTML = "HTML"
    CSS = "CSS"
    PHP = "PHP"
    ELIXIR = "Elixir"
    VERILOG = "Verilog"
    HASKELL = "Haskell"
    LUA = "Lua"
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
    DATABASES = "databases"
    UI_UX = "UI/UX"
    GENERATIVE_AI = "generative-ai"
    DATA_VIS = "data-visualization"
    COMPUTER_GRAPHICS = "computer-graphics"
    GAME_DEV = "game-development"
    CYBERSECURITY = "cybersecurity"
    DATA_STRUCTURES = "data-structures"
    REST_APIS = "rest-apis"
    TESTING = "software-testing"
    MICROCONTROLLERS = "microcontrollers"
    SYSTEMS_PROGRAMMING = "computer-systems-programming"
    HARDWARE = "computer-hardware"
    OS = "operating-systems"
    # Industry Standards
    AWS = "AWS"
    GOOGLE_CLOUD = "Google-Cloud"
    MS_AZURE = "Microsoft-Azure"
    VERCEL = "Vercel"
    POSTGRESQL = "PostgreSQL"
    MONGO_DB = "MongoDB"
    REACT = "React"
    ANGULAR = "Angular"
    VUE = "Vue.js"
    SVELTE = "Svelte"
    BOOTSTRAP = "Bootstrap"
    RAILS = "Ruby-on-Rails"
    DJANGO = "Django"
    FIREBASE = "Firebase"
    GIT = "Git"
    UNIX_LINUX = "Unix/Linux"
    JUPYTER_NOTEBOOKS = "Jupyter-Notebooks"
    NODE_JS = "Node.js"
    DOCKER = "Docker"
    KUBERNETES = "Kubernetes"
    TENSORFLOW = "Tensorflow"
    PYTORCH = "PyTorch"
    FLUTTER = "Flutter"
    REACT_NATIVE = "React-Native"

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
        (SQL, "SQL"),
        (HTML, "HTML"),
        (CSS, "CSS"),
        (PHP, "PHP"),
        (ELIXIR, "Elixir"),
        (VERILOG, "Verilog"),
        (HASKELL, "Haskell"),
        (LUA, "Lua"),
        (FULL_STACK, "Full Stack"),
        (FRONT_END, "Front End"),
        (BACK_END, "Back End"),
        (WEB, "Web"),
        (MOBILE, "Mobile"),
        (DESIGN, "Design"),
        (DEV_OPS, "Dev Ops"),
        (CLOUD, "Cloud"),
        (DATA_SCIENCE, "Data Science"),
        (MACHINE_LEARNING, "Machine Learning"),
        (DATABASES, "Databases"),
        (UI_UX, "UI/UX"),
        (GENERATIVE_AI, "Generative AI"),
        (DATA_VIS, "Data Visualization"),
        (COMPUTER_GRAPHICS, "Computer Graphics"),
        (GAME_DEV, "Game Development"),
        (CYBERSECURITY, "Cybersecurity"),
        (DATA_STRUCTURES, "Data Structures"),
        (REST_APIS, "REST APIs"),
        (TESTING, "Software Testing"),
        (MICROCONTROLLERS, "Microcontrollers"),
        (SYSTEMS_PROGRAMMING, "Computer Systems Programming"),
        (HARDWARE, "Computer Hardware"),
        (OS, "Operating Systems"),
        (AWS, "AWS"),
        (GOOGLE_CLOUD, "Google Cloud"),
        (MS_AZURE, "Microsoft Azure"),
        (VERCEL, "Vercel"),
        (POSTGRESQL, "PostgreSQL"),
        (MONGO_DB, "MongoDB"),
        (REACT, "React"),
        (ANGULAR, "Angular"),
        (VUE, "Vue.js"),
        (SVELTE, "Svelte"),
        (BOOTSTRAP, "Bootstrap"),
        (RAILS, "Ruby on Rails"),
        (DJANGO, "Django"),
        (FIREBASE, "Firebase"),
        (GIT, "Git"),
        (UNIX_LINUX, "Unix/Linux"),
        (JUPYTER_NOTEBOOKS, "Jupyter Notebooks"),
        (NODE_JS, "Node.js"),
        (DOCKER, "Docker"),
        (KUBERNETES, "Kubernetes"),
        (TENSORFLOW, "Tensorflow"),
        (PYTORCH, "PyTorch"),
        (FLUTTER, "Flutter"),
        (REACT_NATIVE, "React Native"),
    )
    # SKILLS
    technology_experience = forms.MultipleChoiceField(
        label="What technical skills do you have?",
        help_text="Select all that apply",
        choices=TECHNOLOGY_EXPERIENCE,
        required=False,
    )

    VEGAN = "Vegan"
    VEGETARIAN = "Vegetarian"
    NO_BEEF = "No-Beef"
    NO_PORK = "No-Pork"
    HALAL = "Halal"
    KOSHER = "Kosher"
    GLUTEN_FREE = "Gluten-Free"
    FOOD_ALLERGY = "Food-Allergy"
    OTHER_DIETARY_RESTRICTION = "Other"

    DIETARY_RESTRICTIONS = (
        (VEGAN, "Vegan"),
        (VEGETARIAN, "Vegetarian"),
        (NO_BEEF, "No Beef"),
        (NO_PORK, "No Pork"),
        (HALAL, "Halal"),
        (KOSHER, "Kosher"),
        (GLUTEN_FREE, "Gluten-Free"),
        (FOOD_ALLERGY, "Food Allergy"),
        (OTHER_DIETARY_RESTRICTION, "Other"),
    )

    dietary_restrictions = forms.MultipleChoiceField(
        label="Do you have any dietary restrictions?",
        help_text="Select all that apply",
        choices=DIETARY_RESTRICTIONS,
        required=False,
    )

    # address = AddressField(
    #     help_text="You will not receive swag and prizes without an address",
    #     required=False,
    # )

    def __init__(self, *args, **kwargs):
        if kwargs.get("instance"):
            kwargs["initial"] = {
                "technology_experience": ast.literal_eval(
                    kwargs.get("instance").technology_experience or "[]"
                ),
                "dietary_restrictions": ast.literal_eval(
                    kwargs.get("instance").dietary_restrictions or "[]"
                ),
            }

        super().__init__(*args, **kwargs)

        photo_agreement = "I grant permission for TAMUhack to use my name, likeness, voice, and any photographs, video recordings, or audio recordings taken during the event 'TAMUhack 2025' for promotional and media purposes, including but not limited to publications, websites, social media, and press releases."
        accessibilities = "Please check this box you would like our team to follow up with you personally to discuss your accessibility accommodations during this event."

        self.fields["agree_to_photos"].label = mark_safe(photo_agreement)
        self.fields["accessibility_requirements"].label = mark_safe(accessibilities)

        self.fields["agree_to_coc"].label = mark_safe(
            'I agree to the <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf">MLH Code of Conduct</a>'
        )

        mlh_stuff = (
            f"I authorize {settings.ORGANIZER_NAME} to share my application/registration information for"
            " event administration, ranking, MLH administration, pre- and post-event informational e-mails,"
            'and occasional messages about hackathons in-line with the <a href="https://mlh.io/privacy">MLH'
            ' Privacy Policy</a>. I further agree to the terms of both the <a href="https://github.com/MLH'
            '/mlh-policies/tree/master/prize-terms-and-conditions">MLH Contest Terms and Conditions</a>'
            ' and the <a href="https://mlh.io/privacy">MLH Privacy Policy</a>'
        )

        mlh_newsletter = "I authorize MLH to send me occasional emails about relevant events, career opportunities, and community announcements."
        self.fields["agree_to_mlh_stuff"].label = mark_safe(mlh_stuff)
        self.fields["signup_to_mlh_newsletter"].label = mark_safe(mlh_newsletter)

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
        major = self.cleaned_data.get("major")
        if major:
            major_other = self.cleaned_data.get("major_other")
            if major == "Other" and not major_other:
                msg = forms.ValidationError(
                    'Please fill out this field or choose "Other".'
                )
                self.add_error("major_other", msg)
        return self.cleaned_data

    class Meta:
        model = application_models.Application
        widgets = {
            "is_adult": forms.CheckboxInput,
            "agree_to_coc": forms.CheckboxInput,
            "agree_to_mlh_stuff": forms.CheckboxInput,
            "signup_to_mlh_newsletter": forms.CheckboxInput,
            "agree_to_photos": forms.CheckboxInput,
            "accessibility_requirements": forms.CheckboxInput,
            "travel_reimbursement": forms.CheckboxInput,
            "tamu_email": forms.EmailInput(attrs={"placeholder": "netid@tamu.edu"}),
            "extra_links": forms.TextInput(
                attrs={
                    "placeholder": "ex. GitHub, Devpost, personal website, LinkedIn, etc."
                }
            ),
        }

        fields = [
            "first_name",
            "last_name",
            "age",
            "phone_number",
            "country",
            "school",
            "school_other",
            "tamu_email",
            "major",
            "major_other",
            "classification",
            "grad_year",
            "level_of_study",
            "gender",
            "gender_other",
            "race",
            "race_other",
            "num_hackathons_attended",
            "technology_experience",
            "wares",
            "dietary_restrictions",
            "has_team",
            "wants_team",
            "shirt_size",
            # "address",
            "resume",
            "extra_links",
            "question1",
            # "question2",
            # "question3",
            "additional_accommodations",
            "accessibility_requirements",
            "emergency_contact_name",
            "emergency_contact_relationship",
            "emergency_contact_phone",
            "emergency_contact_email",
            "notes",
            "agree_to_photos",
            "agree_to_coc",
            "agree_to_mlh_stuff",
            "signup_to_mlh_newsletter",
            "is_adult",
        ]
