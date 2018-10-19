from django.shortcuts import render
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

def home(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'sign_up.html')

def dash(request):
    dashboard.status(request)
