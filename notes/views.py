from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import CustomUserCreationForm, CustomUserLoginForm, NotesForm, TagsForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Notes, Tags, CustomUser, NotesTags
from django.urls import reverse
from django.forms import formset_factory, modelform_factory


def home(request):
    return render(request, "index.html")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful")
            return redirect("home")
        else:
            messages.error(request, "Failed to register")
    else:
        form = CustomUserCreationForm()
    return render(request, template_name="registration.html", context={"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = CustomUserLoginForm(data=request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Wrong email or password")
    else:
        form = CustomUserLoginForm()
    return render(request, "login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("login")


def view_notes(request):
    if request.user.is_authenticated:
        notes = Notes.objects.filter(user=request.user).prefetch_related("tags_set")
        return render(request, "view_notes.html", {"notes": notes})


def view_all_public_notes(request):
    if request.user.is_authenticated:
        notes = Notes.objects.filter(is_public=True).prefetch_related("tags_set")
        return render(request, "view_all_public_notes.html", {"notes": notes})


def note_detail_view(request, pk):
    note = get_object_or_404(Notes, pk=pk)
    return render(request, "note_detail_view.html", {"note": note})


def update_note(request, pk):
    if not request.user.is_authenticated:
        return HttpResponse('Page not found')
    data = {
        "form-TOTAL_FORMS": "1",
        "form-INITIAL_FORMS": "0",
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "10",
    }
    obj = get_object_or_404(Notes.objects.prefetch_related("tags_set"), user=request.user, pk=pk)
    form = NotesForm(request.POST or None, instance=obj)

    TagsFormSet = formset_factory(TagsForm)
    qs = obj.tags_set.all()
    data["form-TOTAL_FORMS"] = str(qs.count())
    for i in range(len(qs)):
        data[f"form-{i}-tag"] = qs[i]
    formset = TagsFormSet(request.POST or data)

    if request.method == "POST":
        if all([form.is_valid(), formset.is_valid()]):
            if form.has_changed():
                form.save()
            tags_list = []
            for f in formset:
                if bool(f.cleaned_data.get("tag")):
                    tag_obj, created = Tags.objects.get_or_create(tag=f.cleaned_data["tag"])
                    tags_list.append(tag_obj)
            obj.tags_set.set(tags_list)
            obj.save()
        return redirect(reverse("detail_view", args=[obj.pk]))
    return render(request, "create_note.html", {"form": form, "formset": formset})


def create_note_view(request):
    data = {
        "form-TOTAL_FORMS": "1",
        "form-INITIAL_FORMS": "0",
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "10",
    }
    TagsFormSet = formset_factory(TagsForm)
    if request.method == "POST" and request.user.is_authenticated:
        user_obj = get_object_or_404(CustomUser, email=request.user)
        form = NotesForm(data=request.POST)
        formset = TagsFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            note = Notes.objects.create(user=user_obj, **form.cleaned_data)

            if not any(bool(f.cleaned_data) for f in formset):
                """if all tags empty - create note and redirect to detail view page"""
                return redirect(reverse("detail_view", args=[note.pk]))

            tags_list = []
            for f in formset:
                if bool(f.cleaned_data.get("tag")):
                    tag_obj, created = Tags.objects.get_or_create(tag=f.cleaned_data["tag"])
                    tags_list.append(tag_obj)
            note.tags_set.add(*tags_list)
            return redirect(reverse("detail_view", args=[note.pk]))

    else:
        formset = TagsFormSet(data)
        form = NotesForm()
    return render(request, "create_note.html", {"form": form, "formset": formset})