from MainApp.models import NodeModel
from django.contrib import messages
from django.views import View
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import CloudUserAuthForm
from .forms import CloudUserLoginForm


class RegistrationView(CreateView):
    form_class = CloudUserAuthForm 
    template_name = 'registration.html'
    success_url = reverse_lazy('login')
    all_nodes = NodeModel.objects.all()

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            node_domain, node_id = self.min_user_quantity_domain()
            node = NodeModel.objects.get(id=node_id)
            node.user_quantity += 1
            node.save()

            user.node_domain = node_domain
            user.save()
            login(self.request, user)
            return redirect('MainApp:profile')
        return response

    def min_user_quantity_domain():
        min_user_quantity = float('inf')
        min_user_quantity_node = None

        for node in self.all_nodes:
            user_quantity = node.user_quantity
            if user_quantity < min_user_quantity:
                min_user_quantity = user_quantity
                min_user_quantity_node = node
        return min_user_quantity_node, node_id


class LoginView(View):
    form_class = CloudUserLoginForm
    template_name = 'login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid credentials')
        return render(request, self.template_name, {'form': form})



def NodeConnection():
    if request.method == 'POST':
        domain = request.POST.get('domain')
        if domain:
            node = NodeModel(node_domain=domain, user_quantity='0')
            node.save
            return HttpResponse('Domain saved successfully.')
        else:
            return HttpResponse('No domain value found in the POST request.')
    else:
        return HttpResponse('Invalid request method.')


@csrf_protect
def home_render(request):
    return render(request, 'main/home.html')


@login_required
def profile_render(request):
    return render(request, 'registration/profile.html')

