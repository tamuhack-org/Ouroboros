import ast
import json

from django import forms
from django.conf import settings
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
        (REACT_NATIVE, "React Native")
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
        (GLUTEN_FREE, "Gluten-Free")
        (FOOD_ALLERGY, "Food Allergy")
        (OTHER_DIETARY_RESTRICTION, "Other")
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
        self.fields["agree_to_coc"].label = mark_safe(
            'I agree to the <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf">MLH Code of Conduct</a>'
        )

        mlh_stuff = (
            f"I authorize {settings.EVENT_NAME} to share my application/registration information for"
            " event administration, ranking, MLH administration, pre- and post-event informational e-mails,"
            'and occasional messages about hackathons in-line with the <a href="https://mlh.io/privacy">MLH'
            ' Privacy Policy</a>. I further agree to the terms of both the <a href="https://github.com/MLH'
            '/mlh-policies/tree/master/prize-terms-and-conditions">MLH Contest Terms and Conditions</a>'
            ' and the <a href="https://mlh.io/privacy">MLH Privacy Policy</a>'
        )

        self.fields["agree_to_mlh_stuff"].label = mark_safe(mlh_stuff)

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
            "agree_to_mlh_stuff": forms.CheckboxInput,
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
            "notes",
            "agree_to_coc",
            "agree_to_mlh_stuff",
            "is_adult",
        ]
