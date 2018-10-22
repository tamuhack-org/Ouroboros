from django.contrib import admin
from .models import Hacker, Application, Confirmation, Team
from django import forms


class HackerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('User Information', {'fields': ['first_name','last_name','email','username','password']}),
        ('Advanced',         {'fields': ['is_superuser','is_staff','is_active'], 'classes': ['collapse']}),
    ]


class ApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'
        widgets = {
            'gender':forms.RadioSelect,
            'classification':forms.RadioSelect,
            'grad_year':forms.RadioSelect,
            'status':forms.RadioSelect,
        }


class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    fieldsets = [
        ('Related Objects',         {'fields': ['hacker']}),
        ('Personal Information',    {'fields': ['gender','major','classification','grad_year']}),
        ('Free Response Questions', {'fields': ['interests','essay','notes']}),
        ('Status',                  {'fields': ['approved']}),
    ]


class ConfirmationAdminForm(forms.ModelForm):
    class Meta:
        model = Confirmation
        fields = '__all__'
        widgets = {
            'shirt_size':forms.RadioSelect,
            'dietary_restrictions':forms.RadioSelect,
        }

class ConfirmationAdmin(admin.ModelAdmin):
    form = ConfirmationAdminForm
    fieldsets = [
        ('Related Objects',        {'fields': ['hacker','team']}),
        ('Logistical Information', {'fields': ['shirt_size','dietary_restrictions','travel_reimbursement_required','notes']}),
    ]


class TeamAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Team Name', {'fields': ['name']}),
    ]

admin.site.register(Hacker, HackerAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Confirmation, ConfirmationAdmin)
admin.site.register(Team, TeamAdmin)