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
    return render(request, 'sign_up.html')
    if request.method == 'POST':
        form = UserCreationForm(request.POST) #TODO: change to custom creation once it is made 
        if form.is_valid():
            form.save()
            return redirect('/status')
    else:
        form = UserCreationForm()

        args = {'form': form}
        return render(request, 'sign_up.html', args)

class dashboard:
    def status(request):
        return render(request, 'status.html')
    def application(request):
        return render(request, 'application.html')
    def team(request):
        return render(request, 'team.html')
    def information(request):
        return render(request, 'information.html')
<<<<<<< HEAD
    def logout(request):
        # do stuff to end session
        return redirect('/')
=======
>>>>>>> 0c6238e24046e80d4bed1868ecd6695e91595741

def dash(request):
    dashboard.status(request)
