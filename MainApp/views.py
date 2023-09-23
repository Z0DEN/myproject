from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def home_render(request):
    return render(request, 'main/home.html')

@login_required
def profile_render(request):
    return render(request, 'registration/profile.html')
