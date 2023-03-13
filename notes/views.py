from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import CustomUserCreationForm, CustomUserLoginForm, NotesForm, TagsForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Notes, Tags, CustomUser

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


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserLoginForm(data=request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Wrong email or password')
    else:
        form = CustomUserLoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


def create_note_view(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user_obj = get_object_or_404(CustomUser, email=request.user)
        form = NotesForm(data=request.POST or None)
        form2 = TagsForm(data=request.POST or None)

        if form.is_valid() and form2 is None:
            note_obj = Notes.objects.create(user=user_obj, **form.cleaned_data)
            note_obj.save()
            return redirect('home')

        if form2.is_valid() and form2.is_valid() and form2 is not None:
            note_obj = Notes.objects.create(user=user_obj, **form.cleaned_data)
            tags: str = form2.cleaned_data['tag']
            tag_list: list = (tags.strip()).split('#')
            parsed_tags: list[str] = []
            for i in tag_list:  # parsing and creating a list of tags
                if i.strip() != "":
                    parsed_tags.append(" ".join(i.split()).lower())
            for t in parsed_tags:  # creating/getting a tag and adding relation to Notes instance
                tag, created = Tags.objects.get_or_create(tag=t)
                note_obj.tags_set.add(tag)
            note_obj.save()
            return redirect('home')

        return render(request, 'create_note.html', {'form': form, 'form2': form2})
    else:
        form = NotesForm()
        form2 = TagsForm()
    return render(request, 'create_note.html', {'form': form, 'form2': form2})
