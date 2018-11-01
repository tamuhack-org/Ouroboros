from django.shortcuts import render, redirect
from django.views.generic import base as base_views
from django.views import generic as generic_views
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
# Create your views here.



def home(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'signup.html')
    if request.method == 'POST':
        form = SignupForm(request.POST) #TODO: change to custom creation once it is made 
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/application')
    else:
        form = SignupForm()

        args = {'form': form}
        return render(request, 'signup.html', args)

class dashboard:
    def status(request):
        return render(request, 'dashboard/status.html')
    def application(request):
        return render(request, 'dashboard/application.html')
    def team(request):
        return render(request, 'dashboard/team.html')
    def information(request):
        return render(request, 'dashboard/information.html')
    def logout(request):
        # do stuff to end session
        return redirect('/')

def dash(request):
    dashboard.status(request)
