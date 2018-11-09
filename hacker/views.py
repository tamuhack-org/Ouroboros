from django.shortcuts import render, redirect
from django.views.generic import base as base_views
from django.views import generic as generic_views
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


def home(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST) #TO-DO: change to custom creation once it is made 
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

class dashboard(LoginRequiredMixin):
    login_url = '/auth/login/'
    redirect_field_name = '/status'
    
    @login_required
    def status(request):
        return render(request, 'dashboard/status.html')
    
    @login_required
    def application(request):
        redirect_field_name = '/application'
        return render(request, 'dashboard/application.html')
    
    @login_required
    def team(request):
        redirect_field_name = '/team'
        return render(request, 'dashboard/team.html')
    
    @login_required
    def information(request):
        redirect_field_name = '/information'
        return render(request, 'dashboard/information.html')

@login_required
def dash(request):
    dashboard.status(request)
