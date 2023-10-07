from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.models import User
from .forms import RegistrationForm
from .models import CloudUser


class RegistrationView3(CreateView):
    form_class = RegistrationForm
    template_name = 'registration.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(self.request, username=username, password=password, node_domain='node1')
        print(username, password, user)
        if user is not None:
            login(self.request, user)
            return redirect('MainApp:profile')
        return response






class RegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = CloudUser(username=form.cleaned_data['username'], password=form.cleaned_data['password1'], node_domain='node1')
        user.save()
        print('сохранение пользователя прошло успешно')
        print(user)
        print(form.cleaned_data['username'], form.cleaned_data['password1'], 'node1')
        return super().form_valid(form)




def get_domain():
    node_domain = 'node1'
    print(node_domain)
    return node_domain

@csrf_protect
def home_render(request):
    return render(request, 'main/home.html')


@login_required
def profile_render(request):
    return render(request, 'registration/profile.html')

