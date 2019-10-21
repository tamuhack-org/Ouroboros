from django import forms

from team.models import Team


class CreateTeamForm(forms.ModelForm):
    """
    Creates a new Team. See superclass documentation for further details.
    """

    class Meta:
        model = Team
        widgets = {"name": forms.TextInput(attrs={"placeholder": "Team Name"})}
        fields = ["name"]


class JoinTeamForm(forms.Form):
    """
    A generic Django form. The "id" field is used to look up the corresponding Team.
    """

    id = forms.UUIDField(label="Use the Team ID to join an existing team")
