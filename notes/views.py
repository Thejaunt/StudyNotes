from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.contrib import messages


def home(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful')
            return redirect('home')
        else:
            messages.error(request, 'Failed to register')
    else:
        form = CustomUserCreationForm()
    return render(request, template_name='registration.html', context={'form': form})
