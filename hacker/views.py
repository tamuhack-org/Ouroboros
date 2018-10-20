from django.shortcuts import render
from django.views.generic import base as base_views
from django.views import generic as generic_views
from django.contrib.auth import authenticate, login

# Create your views here.

class dashboard:
    def status(request):
        return render(request, 'status.html')
    def application(request):
        return render(request, 'application.html')
    def team(request):
        return render(request, 'team.html')
    def information(request):
        return render(request, 'information.html')

def dash(request):
    dashboard.status(request)
