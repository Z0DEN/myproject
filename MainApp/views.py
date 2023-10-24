from django.http import HttpResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.generic import CreateView
from django.urls import reverse_lazy
from MainApp.models import NodeModel
from .forms import CloudUserAuthForm, CloudUserLoginForm

class RegistrationView(CreateView):
    form_class = CloudUserAuthForm
    template_name = 'registration.html'
    success_url = reverse_lazy('MainApp:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            node = self.min_user_quantity_domain()
            node_domain = node.node_domain
            node.user_quantity += 1
            node.save()

            user.node_domain = node_domain
            user.save()
            login(self.request, user)
            return redirect('MainApp:profile')
        return response

    def min_user_quantity_domain(self):
        min_user_quantity = float('inf')
        min_user_quantity_node = None

        for node in NodeModel.objects.all():
            user_quantity = node.user_quantity
            if user_quantity < min_user_quantity:
                min_user_quantity = user_quantity
                min_user_quantity_node = node
        return min_user_quantity_node


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
                return redirect('MainApp:home')
            else:
                form.add_error(None, 'Invalid credentials')
        return render(request, self.template_name, {'form': form})


@csrf_exempt
def NodeConnection(request):
    if request.method == 'POST':

        node_domain = request.POST['node_domain']
        ip_address = request.POST['ip_address']

        if not node_domain:
            return JsonResponse({'success': False, 'message': 'Неверное доменное имя'})
        if not ip_address:
            return JsonResponse({'success': False, 'message': 'Неверный ip адрес'})

        new_node = NodeModel(
            node_domain=node_domain,
            ip_address=ip_address,
            user_quantity=0,
        )

        new_node.save()

        # Add a Content-Type header to the response
        response = JsonResponse({
            'success': True,
            'node_domain': node_domain,
            'ip_address': ip_address,
            'date': date,
        })
        response['Content-Type'] = 'application/json'

        return response

    else:
        print('method=get')
        return HttpResponse('Invalid request method.')


@csrf_protect
def home_render(request):
    return render(request, 'main/home.html')


@login_required
def profile_render(request):
    return render(request, 'registration/profile.html')

