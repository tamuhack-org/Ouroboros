from django.contrib import admin
from .models import Hacker, Application, Confirmation, Team
from django import forms
import datetime


''' `Hacker` '''
def make_checked_in(modeladmin, request, queryset): # Needs to be Tested!!!
    queryset.update(checked_in=True)
    queryset.update(checked_in_datetime=datetime.datetime.now())

class HackerAdmin(admin.ModelAdmin):
    list_display = ('username','email','first_name', 'last_name', 'is_active', 'is_staff', 'checked_in')
    fieldsets = [
        ('User Information', {'fields': ['first_name','last_name','email','username','password']}),
        ('Advanced',         {'fields': ['is_superuser','is_staff','is_active'], 'classes': ['collapse']}),
    ]

    make_checked_in.short_description = "Check-In Selected Hackers"
    actions = [make_checked_in]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

#    def has_delete_permission(self, request, obj=None):
#        return False
    
''' `Application` '''
def make_approved(modeladmin, request, queryset): # Needs to be Tested!!!
    queryset.update(approved=True)

def make_rejected(self, request, queryset): # Needs to be Tested!!!
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
        ('Personal Information',    {'fields': ['gender','major','classification','grad_year']}),
        ('Free Response Questions', {'fields': ['interests','essay','notes']}),
        ('Status',                  {'fields': ['approved']}),
    ]

    make_approved.short_description = "Approve Selected Applications"
    make_rejected.short_description = "Reject Selected Applications"
    actions = [make_approved, make_rejected]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

#    def has_delete_permission(self, request, obj=None):
#        return False


''' `Confirmation` '''    
class ConfirmationAdminForm(forms.ModelForm):
    class Meta:
        model = Confirmation
        fields = ['shirt_size', 'dietary_restrictions', 'notes', 'team', 'hacker']
        widgets = {
            'shirt_size':forms.RadioSelect,
            #'dietary_restrictions':forms.RadioSelect,
        }
    '''  
    def __init__(self, *args, **kwargs):
        super(ConfirmationAdminForm, self).__init__(*args, **kwargs)
        self.fields['shirt_size'].empty_label = None
        # following line needed to refresh widget copy of choice list
        self.fields['shirt_size'].widget.choices = self.fields['shirt_size'].choices
        self.fields['shirt_size'].required = True
    '''
        
class ConfirmationAdmin(admin.ModelAdmin):
    form = ConfirmationAdminForm
    list_display = ('shirt_size', 'dietary_restrictions')
    fieldsets = [
        ('Related Objects',        {'fields': ['hacker','team']}),
        ('Logistical Information', {'fields': ['shirt_size','dietary_restrictions','notes']}),
    ]
    
    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


''' `Team` '''
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