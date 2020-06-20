from django import forms
from django.utils.safestring import mark_safe

from application import models as application_models, models
from application.models import School


class ApplicationModelForm(forms.ModelForm):
    gender_other = forms.CharField(
        label='If you chose "Prefer to self-describe", please elaborate.',
        required=False,
    )
    race_other = forms.CharField(
        label='If you chose "Prefer to self-describe", please elaborate.',
        required=False,
    )
    school = forms.ModelChoiceField(
        School.objects.all(), label="What school do you go to?",
    )
    school_other = forms.CharField(
        label='If you chose "Other", please enter your school\'s name here.',
        required=False,
    )
    MAJORS = (
        ("Accounting", "Accounting"),
        ("Aerospace Engineering", "Aerospace Engineering"),
        ("Agricultural Economics", "Agricultural Economics"),
        (
            "Agricultural Leadership, Education, and Communications",
            "Agricultural Leadership, Education, and Communications",
        ),
        ("Agronomy", "Agronomy"),
        ("Alternative Dispute Resolution", "Alternative Dispute Resolution"),
        ("Analytics", "Analytics"),
        ("Animal Science", "Animal Science"),
        ("Anthropology", "Anthropology"),
        ("Applied Mathematics", "Applied Mathematics"),
        ("Architecture", "Architecture"),
        ("Astronomy", "Astronomy"),
        ("Atmospheric Sciences", "Atmospheric Sciences"),
        ("Biochemistry and Biophysics", "Biochemistry and Biophysics"),
        (
            "Biological and Agricultural Engineering",
            "Biological and Agricultural Engineering",
        ),
        ("Biology", "Biology"),
        ("Biomedical Engineering", "Biomedical Engineering"),
        ("Biomedical Sciences", "Biomedical Sciences"),
        ("Business Law", "Business Law"),
        ("Chemical Engineering", "Chemical Engineering"),
        ("Chemistry", "Chemistry"),
        ("Civil Engineering", "Civil Engineering"),
        ("Civil Litigation", "Civil Litigation"),
        ("Commercial Law", "Commercial Law"),
        ("Communications", "Communications"),
        ("Computer Science & Engineering", "Computer Science & Engineering"),
        ("Construction Science", "Construction Science"),
        ("Criminal Law and Procedure", "Criminal Law and Procedure"),
        ("Data Science & Analytics", "Data Science & Analytics"),
        ("Dental Hygiene", "Dental Hygiene"),
        ("Diagnostic Sciences", "Diagnostic Sciences"),
        ("Economics", "Economics"),
        ("Ecosystem Science and Management", "Ecosystem Science and Management"),
        (
            "Educational Administration & Human Resource Development",
            "Educational Administration & Human Resource Development",
        ),
        ("Educational Psychology", "Educational Psychology"),
        ("Electrical Engineering", "Electrical Engineering"),
        ("Electronic Systems Engineering", "Electronic Systems Engineering"),
        ("Endodontics", "Endodontics"),
        ("Energy", "Energy"),
        ("Energy Law", "Energy Law"),
        (
            "Engineering Technology & Industrial Distribution",
            "Engineering Technology & Industrial Distribution",
        ),
        ("English", "English"),
        ("Entomology", "Entomology"),
        ("Environmental Law", "Environmental Law"),
        ("Estate Planning", "Estate Planning"),
        ("Family Law", "Family Law"),
        ("Family Nurse Practitioner", "Family Nurse Practitioner"),
        ("Finance", "Finance"),
        ("Food Science", "Food Science"),
        ("Forensic Health Care", "Forensic Health Care"),
        ("Forensic Nursing", "Forensic Nursing"),
        ("General Dentistry", "General Dentistry"),
        ("General Practice", "General Practice"),
        ("Genetics", "Genetics"),
        ("Geography", "Geography"),
        ("Geology", "Geology"),
        ("Geoscience", "Geoscience"),
        ("Health & Kinesiology", "Health & Kinesiology"),
        ("Health Education", "Health Education"),
        ("Health Law", "Health Law"),
        ("Hispanic Studies", "Hispanic Studies"),
        ("History", "History"),
        ("Horticultural Sciences", "Horticultural Sciences"),
        ("Humanities in Medicine", "Humanities in Medicine"),
        ("IP and Technology Law", "IP and Technology Law"),
        ("Immigration Law", "Immigration Law"),
        (
            "Industrial and/or Systems Engineering",
            "Industrial and/or Systems Engineering",
        ),
        ("Information Science", "Information Science"),
        (
            "Information and Operations Management",
            "Information and Operations Management",
        ),
        ("International Affairs", "International Affairs"),
        ("International Studies", "International Studies"),
        (
            "Landscape Architecture & Urban Planning",
            "Landscape Architecture & Urban Planning",
        ),
        ("Management Information Systems", "Management Information Systems"),
        ("Marketing", "Marketing"),
        ("Material Science", "Material Science"),
        ("Mathematics", "Mathematics"),
        ("Mechanical Engineering", "Mechanical Engineering"),
        ("Medical Education", "Medical Education"),
        ("Medical Physiology", "Medical Physiology"),
        (
            "Microbial Pathogenesis and Immunology",
            "Microbial Pathogenesis and Immunology",
        ),
        ("Molecular & Cellular Medicine", "Molecular & Cellular Medicine"),
        ("Neuroscience", "Neuroscience"),
        ("Nuclear Engineering", "Nuclear Engineering"),
        ("Nursing", "Nursing"),
        ("Nursing Education", "Nursing Education"),
        ("Nutrition and Food Science", "Nutrition and Food Science"),
        ("Ocean Engineering", "Ocean Engineering"),
        ("Oceanography", "Oceanography"),
        ("Oil and Gas Law", "Oil and Gas Law"),
        ("Oral and Maxillofacial Surgery", "Oral and Maxillofacial Surgery"),
        ("Orthodontics", "Orthodontics"),
        ("Pediatric Dentistry", "Pediatric Dentistry"),
        ("Performance Studies", "Performance Studies"),
        ("Periodontics", "Periodontics"),
        ("Petroleum Engineering", "Petroleum Engineering"),
        ("Philosophy", "Philosophy"),
        ("Physics", "Physics"),
        ("Plant Pathology and Microbiology", "Plant Pathology and Microbiology"),
        ("Political Science", "Political Science"),
        ("Poultry Science", "Poultry Science"),
        ("Primary Care Medicine", "Primary Care Medicine"),
        ("Psychiatry", "Psychiatry"),
        ("Psychology", "Psychology"),
        ("Public Health", "Public Health"),
        ("Public Service and Administration", "Public Service and Administration"),
        ("Real Estate Law", "Real Estate Law"),
        (
            "Recreation, Park and Tourism Sciences",
            "Recreation, Park and Tourism Sciences",
        ),
        ("Restorative Sciences", "Restorative Sciences"),
        ("Sociology", "Sociology"),
        ("Soil and Crop Sciences", "Soil and Crop Sciences"),
        ("Statistics", "Statistics"),
        ("Supply Chain", "Supply Chain"),
        ("Teaching, Learning & Culture", "Teaching, Learning & Culture"),
        ("Veterinary Biology", "Veterinary Biology"),
        ("Visualization", "Visualization"),
        ("Water Law", "Water Law"),
        ("Wildlife and Fisheries Sciences", "Wildlife and Fisheries Sciences"),
        ("Workplace Law", "Workplace Law"),
        ("Other", "Other"),
    )
    majors = forms.MultipleChoiceField(label="What's your major(s)?", choices=MAJORS)
    minors = forms.MultipleChoiceField(
        label="What's your minor(s)?", choices=MAJORS, required=False
    )
    STATES = (
        ("", "---------"),
        ("Alabama", "Alabama"),
        ("Alaska", "Alaska"),
        ("Arizona", "Arizona"),
        ("Arkansas", "Arkansas"),
        ("California", "California"),
        ("Colorado", "Colorado"),
        ("Connecticut", "Connecticut"),
        ("Delaware", "Delaware"),
        ("Florida", "Florida"),
        ("Georgia", "Georgia"),
        ("Hawaii", "Hawaii"),
        ("Idaho", "Idaho"),
        ("Illinois", "Illinois"),
        ("Indiana", "Indiana"),
        ("Iowa", "Iowa"),
        ("Kansas", "Kansas"),
        ("Kentucky", "Kentucky"),
        ("Louisiana", "Louisiana"),
        ("Maine", "Maine"),
        ("Maryland", "Maryland"),
        ("Massachusetts", "Massachusetts"),
        ("Michigan", "Michigan"),
        ("Minnesota", "Minnesota"),
        ("Mississippi", "Mississippi"),
        ("Missouri", "Missouri"),
        ("Montana", "Montana"),
        ("Nebraska", "Nebraska"),
        ("Nevada", "Nevada"),
        ("New Hampshire", "New Hampshire"),
        ("New Jersey", "New Jersey"),
        ("New Mexico", "New Mexico"),
        ("New York", "New York"),
        ("North Carolina", "North Carolina"),
        ("North Dakota", "North Dakota"),
        ("Ohio", "Ohio"),
        ("Oklahoma", "Oklahoma"),
        ("Oregon", "Oregon"),
        ("Pennsylvania", "Pennsylvania"),
        ("Rhode Island", "Rhode Island"),
        ("South Carolina", "South Carolina"),
        ("South Dakota", "South Dakota"),
        ("Tennessee", "Tennessee"),
        ("Texas", "Texas"),
        ("Utah", "Utah"),
        ("Vermont", "Vermont"),
        ("Virginia", "Virginia"),
        ("Washington", "Washington"),
        ("West Virginia", "West Virginia"),
        ("Wisconsin", "Wisconsin"),
        ("Wyoming", "Wyoming"),
    )
    physical_location = forms.ChoiceField(
        label="Where will you be participating from?", choices=STATES
    )
    DATASCIENCE_EXPERIENCE = (
        ("", "---------"),
        ("0", "None"),
        ("1", "Dabbled here and there"),
        ("2", "Some side projects and/or classes"),
        ("3", "Data science specific internship"),
        ("4", "Years of industry experience"),
    )
    datascience_experience = forms.ChoiceField(
        label="How would you rank your experience with data science?",
        choices=DATASCIENCE_EXPERIENCE,
    )
    TECHNOLOGY_EXPERIENCE = (
        ("Excel", "Excel"),
        ("Python", "Python"),
        ("Tableau", "Tableau"),
        ("TensorFlow", "TensorFlow"),
        ("Pytorch", "Pytorch"),
        ("R", "R"),
        ("SQL", "SQL"),
        ("PyTorch", "PyTorch"),
        ("Keras", "Keras"),
        ("Pandas", "Pandas"),
        ("NumPy", "NumPy"),
        ("Scikit-learn", "Scikit-learn"),
        ("MATLAB", "MATLAB"),
    )
    technology_experience = forms.MultipleChoiceField(
        label="What technologies do you have experience with?",
        choices=TECHNOLOGY_EXPERIENCE,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["agree_to_mlh_policies"].label = mark_safe(
            'I have read and agree to the <a target="_blank" href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf">MLH Code of Conduct</a> and the <a target="_blank" href="https://github.com/MLH/mlh-policies/blob/master/prize-terms-and-conditions/contest-terms.md">MLH Contest Terms and Conditions</a>.'
        )
        self.fields["agree_to_privacy"].label = mark_safe(
            'I have read and agree to the <a target="_blank" href="https://mlh.io/privacy">MLH Privacy Policy</a>.'
        )
        self.fields["first_generation"].label = mark_safe(
            "I am a first generation college student."
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
        if gender == models.GENDER_OTHER:
            gender_other = self.cleaned_data.get("gender_other")
            if not gender_other:
                msg = forms.ValidationError(
                    'Please fill out this field or choose "Prefer not to answer".'
                )
                self.add_error("gender_other", msg)
        races = self.cleaned_data.get("race")
        if races:
            race_other = self.cleaned_data.get("race_other")
            if models.RACE_OTHER in races and not race_other:
                msg = forms.ValidationError(
                    "Please fill out this field with the appropriate information."
                )
                self.add_error("race_other", msg)
        return self.cleaned_data

    class Meta:
        model = application_models.Application
        widgets = {
            "is_adult": forms.CheckboxInput,
            "agree_to_mlh_policies": forms.CheckboxInput,
            "agree_to_privacy": forms.CheckboxInput,
            "first_generation": forms.CheckboxInput,
            "extra_links": forms.TextInput(
                attrs={
                    "placeholder": "ex. personal projects, organization website, special circumstances, etc."
                }
            ),
            "github_link": forms.TextInput(
                attrs={"placeholder": "ex. https://github.com/tamu-datathon-org"}
            ),
            "linkedin_link": forms.TextInput(
                attrs={"placeholder": "ex. https://linkedin.com/in/tamudatathon"}
            ),
            "personal_website_link": forms.TextInput(
                attrs={"placeholder": "ex. https://tamudatathon.com"}
            ),
            "instagram_link": forms.TextInput(
                attrs={"placeholder": "ex. https://instagram.com/tamudatathon"}
            ),
            "devpost_link": forms.TextInput(
                attrs={"placeholder": "ex. https://devpost.com/tamudatathon"}
            ),
        }

        fields = [
            "first_name",
            "last_name",
            "github_link",
            "linkedin_link",
            "personal_website_link",
            "instagram_link",
            "devpost_link",
            "resume",
            "referral",
            "learner",
            "volunteer",
            "school",
            "school_other",
            "first_generation",
            "physical_location",
            "majors",
            "minors",
            "classification",
            "grad_year",
            "gender",
            "gender_other",
            "age",
            "race",
            "race_other",
            "num_hackathons_attended",
            "technology_experience",
            "datascience_experience",
            "shirt_size",
            "extra_links",
            "question1",
            "question2",
            "question3",
            "question4",
            "question5",
            "question6",
            "agree_to_mlh_policies",
            "agree_to_privacy",
            "is_adult",
        ]
