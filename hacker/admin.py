from django.contrib import admin
from .models import Hacker, Application, Confirmation, Team


class HackerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('User Information', {'fields': ['first_name','last_name','email','username','password']}),
        ('Advanced',         {'fields': ['is_superuser','is_staff','is_active'], 'classes': ['collapse']}),
    ]

class ApplicationAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Related Objects',         {'fields': ['hacker']}),
        ('Personal Information',    {'fields': ['gender','major','classification','grad_year']}),
        ('Free Response Questions', {'fields': ['interests','essay']}),
        ('Status',                  {'fields': ['approved']}),
    ]

class ConfirmationAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Related Objects',        {'fields': ['hacker','team']}),
        ('Logistical Information', {'fields': ['shirt_size','dietary_restrictions','travel_reimbursement_required']}),
    ]

class TeamAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Team Name', {'fields': ['name']}),
    ]

admin.site.register(Hacker, HackerAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Confirmation, ConfirmationAdmin)
admin.site.register(Team, TeamAdmin)