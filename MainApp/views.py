from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RegistrationForm

class RegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.email = form.cleaned_data['email']
        form.instance.userprofile.phone_number = form.cleaned_data['phone_number']
        return super().form_valid(form)

@csrf_protect
def home_render(request):
    return render(request, 'main/home.html')

@login_required
def profile_render(request):
    return render(request, 'registration/profile.html')

