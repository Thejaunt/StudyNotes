from django.shortcuts import render, redirect, get_object_or_404
from .forms import NotesForm, TagsForm
from .models import Notes, Tags, CustomUser
from django.urls import reverse
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.db.models import Count


def home(request):
    return render(request, "index.html")


@login_required
def profile_view(request):
    notes = Notes.objects.prefetch_related("tags_set").filter(user=request.user).annotate(tags_count=Count('tags'))
    total_notes = notes.count()
    total_tags = sum(tags.tags_count for tags in notes)
    return render(request, "profile.html", {"total_notes": total_notes, "total_tags": total_tags})


@login_required
def view_personal_notes(request):
    notes = Notes.objects.select_related('user').filter(user=request.user)\
        .prefetch_related("tags_set")\
        .prefetch_related("likes")
    return render(request, "view_notes.html", {"notes": notes})


def view_all_public_notes(request):
    notes = Notes.objects.select_related('user').filter(is_public=True)\
        .prefetch_related("tags_set")\
        .prefetch_related("likes")
    return render(request, "view_notes.html", {"notes": notes})


def public_note_detail_view(request, pk):
    note = get_object_or_404(Notes.objects.select_related('user')
                             .prefetch_related("tags_set")
                             .prefetch_related('likes'),
                             pk=pk, is_public=True)
    return render(request, "note_detail_view.html", {"note": note})


@login_required
def personal_note_detail_view(request, pk):
    note = get_object_or_404(Notes.objects.prefetch_related("tags_set")
                             .prefetch_related("likes")
                             .select_related('user'),
                             user=request.user, pk=pk)
    return render(request, "note_detail_view.html", {"note": note})


@login_required
def update_note(request, pk):
    data = {
        "form-TOTAL_FORMS": "1",
        "form-INITIAL_FORMS": "0",
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "10",
    }
    obj = get_object_or_404(Notes.objects.prefetch_related("tags_set"), user=request.user, pk=pk)
    form = NotesForm(request.POST or None, instance=obj)
    tags_formset = formset_factory(TagsForm)
    qs = obj.tags_set.all()
    data["form-TOTAL_FORMS"] = str(qs.count())
    for i in range(len(qs)):
        data[f"form-{i}-tag"] = qs[i]
    formset = tags_formset(request.POST or data)

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
        return redirect(reverse("personal_detail_view", args=[obj.pk]))
    return render(request, "create_update_note.html", {"form": form, "formset": formset})


@login_required
def create_note_view(request):
    data = {
        "form-TOTAL_FORMS": "1",
        "form-INITIAL_FORMS": "0",
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "10",
    }
    tags_formset = formset_factory(TagsForm)
    if request.method == "POST" and request.user.is_authenticated:
        user_obj = get_object_or_404(CustomUser, email=request.user.email)
        form = NotesForm(data=request.POST)
        formset = tags_formset(request.POST)

        if form.is_valid() and formset.is_valid():
            note = Notes.objects.create(user=user_obj, **form.cleaned_data)

            if not any(bool(f.cleaned_data) for f in formset):
                """if all tags are empty - create note and redirect to detail view page"""
                return redirect(reverse("personal_detail_view", args=[note.pk]))

            tags_list = []
            for f in formset:
                if bool(f.cleaned_data.get("tag")):
                    tag_obj, created = Tags.objects.get_or_create(tag=f.cleaned_data.get("tag"))
                    tags_list.append(tag_obj)
            note.tags_set.add(*tags_list)
            return redirect(reverse("personal_detail_view", args=[note.pk]))

    else:
        formset = tags_formset(data)
        form = NotesForm()
    return render(request, "create_update_note.html", {"form": form, "formset": formset})


@login_required
def delete_note_view(request, pk):
    note = get_object_or_404(Notes.objects.prefetch_related("tags_set"), pk=pk, user=request.user)
    if request.method == "POST":
        note.delete()
        return redirect("view_notes")
    return render(request, "delete_note.html", {"note": note})


@login_required
def like_view(request):
    if request.method == "POST":
        note_id = request.POST.get("note_id")
        note_obj = get_object_or_404(Notes.objects.select_related('user'), id=note_id)
        user = request.user
        if user in note_obj.likes.all():
            note_obj.remove_like(user.id)
        else:
            note_obj.add_like(user.id)

        if request.POST.get("page") == "detail":
            return redirect("public_detail_view", note_obj.id)

    return redirect("public_notes")
