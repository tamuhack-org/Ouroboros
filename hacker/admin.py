import datetime

from django import forms
from django.contrib import admin

from .models import Hacker, Application, Confirmation, Team


def check_in(modeladmin, request, queryset): # Needs to be Tested!!!
    queryset.update(checked_in=True)
    queryset.update(checked_in_datetime=datetime.datetime.now())

class HackerAdmin(admin.ModelAdmin):
    list_display = ('username','email','first_name', 'last_name', 'is_active', 'is_staff', 'checked_in')
    fieldsets = [
        ('User Information', {'fields': ['first_name','last_name','email','username','password']}),
        ('Advanced',         {'fields': ['is_superuser','is_staff','is_active'], 'classes': ['collapse']}),
    ]

    check_in.short_description = "Check-In Selected Hackers"
    actions = [check_in]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

#    def has_delete_permission(self, request, obj=None):
#        return False
    

def approve(modeladmin, request, queryset): # Needs to be Tested!!!
    queryset.update(approved=True)

def reject(self, request, queryset): # Needs to be Tested!!!
    queryset.update(approved=False)

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
    list_display = ('get_last_name','get_first_name','major', 'classification', 'grad_year', 'approved', 'get_is_active')
    fieldsets = [
        ('Related Objects',         {'fields': ['hacker']}),
        ('Personal Information',    {'fields': ['gender','major','classification','grad_year', 'dietary_restrictions', 'tamu_student']}),
        ('Hackathon Information',   {'fields': ['num_hackathons_attended', 'previous_attendant']}),
        ('Free Response Questions', {'fields': ['interests','essay1','notes', 'resume']}),
        ('Status',                  {'fields': ['approved']}),
    ]

    approve.short_description = "Approve Selected Applications"
    reject.short_description = "Reject Selected Applications"
    actions = [approve, reject]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

#    def has_delete_permission(self, request, obj=None):
#        return False


class ConfirmationAdminForm(forms.ModelForm):
    class Meta:
        model = Confirmation
        fields = ['shirt_size', 'notes', 'team', 'hacker']
        widgets = {
            'shirt_size':forms.RadioSelect,
        }

        
class ConfirmationAdmin(admin.ModelAdmin):
    form = ConfirmationAdminForm
    list_display = ('shirt_size', 'notes')
    fieldsets = [
        ('Related Objects',        {'fields': ['hacker','team']}),
        ('Logistical Information', {'fields': ['shirt_size','notes']}),
    ]
    
    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class TeamAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Team Name', {'fields': ['name']}),
    ]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
        


admin.site.register(Hacker, HackerAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Confirmation, ConfirmationAdmin)
admin.site.register(Team, TeamAdmin)