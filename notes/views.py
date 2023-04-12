from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserLoginForm, NotesForm, TagsForm, ProfileImageForm, PasswordSetForm,\
    PassResetForm, ProfileUsernameForm
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from .models import Notes, Tags, CustomUser
from django.urls import reverse
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.db.models.query_utils import Q


def home(request):
    return render(request, "index.html")


def activate(request, uidb64, token):
    usermodel = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = usermodel.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, usermodel.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for email confirmation")
    else:
        messages.error(request, "Activation link is invalid")
    return redirect("home")


def activate_email(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("template_activate_account.html", {
        "user": user.email,
        "domain": get_current_site(request).domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
        "protocol": "https" if request.is_secure() else "http"
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request,
                         f"{user}, please go to your email, {to_email} inbox and click on received activation link to"
                         f" confirm and complete the registration. Note: Check your spam folder.")
    else:
        messages.error(request, f"Problem sending confirmation email to {to_email}, check if you typed it correctly")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get("email"))
            return redirect("home")
        else:
            for key, error in list(form.errors.items()):
                if key == "captcha" and error[0] == "This field is required.":
                    messages.error(request, "You must pass the reCAPTCHA verification")
                    continue
                messages.error(request, "Failed to register")
    else:
        form = CustomUserCreationForm()
    return render(request, template_name="registration.html", context={"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = CustomUserLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
        else:
            for key, error in list(form.errors.items()):
                if key == "captcha" and error[0] == "This field is required.":
                    messages.error(request, "You must pass the reCAPTCHA verification")
                    continue
                messages.error(request, "Wrong email or password")
    else:
        form = CustomUserLoginForm()
    return render(request, "login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def profile_view(request):
    notes = Notes.objects.prefetch_related("tags_set").filter(user=request.user).annotate(tags_count=Count('tags'))
    total_notes = notes.count()
    total_tags = sum(tags.tags_count for tags in notes)
    return render(request, "profile.html", {"total_notes": total_notes, "total_tags": total_tags})


@login_required
def update_profile_img(request):
    user_obj = get_object_or_404(CustomUser, email=request.user.email)
    form = ProfileImageForm(request.POST or None, request.FILES or None, instance=user_obj)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profile image has been updated")
            return redirect('profile')
    return render(request, "update_profile_img.html", {"form": form})


@login_required()
def update_profile_name(request):
    user_obj = get_object_or_404(CustomUser, email=request.user.email)
    form = ProfileUsernameForm(request.POST or None, instance=user_obj)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Username has been updated")
            return redirect("profile")
    return render(request, "update_profile_name.html", {"form": form})


@login_required
def password_change(request):
    user = request.user
    if request.method == "POST":
        form = PasswordSetForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password has been changed")
            return redirect("login")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = PasswordSetForm(user)
    return render(request, "password_reset_confirm.html", {"form": form})


def password_reset_request(request):
    if request.method == "POST":
        form = PassResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get("email")
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset"
                message = render_to_string("template_reset_password.html", {
                    "user": associated_user,
                    "domain": get_current_site(request).domain,
                    "uid": urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    "token": account_activation_token.make_token(associated_user),
                    "protocol": "https" if request.is_secure() else "http"
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                    """
                        Password reset sent.
                        We've emailed you instructions for setting your password,
                        if an account exists with the email you entered.
                        You should receive them shortly. If you don't receive an email,
                        please make sure you've entered the  address you registered with, and check your spam folder.
                    """
                                     )
                else:
                    messages.error(request, "Problem sending reset password email")
            return redirect("home")

        for key, error in list(form.errors.items()):
            if key == "captcha" and error[0] == "This field is required.":
                messages.error(request, "You must pass the reCAPTCHA verification")
                continue

    form = PassResetForm()
    return render(request, "password_reset.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    usermodel = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = usermodel.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, usermodel.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == "POST":
            form = PasswordSetForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been reset")
                return redirect("login")
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = PasswordSetForm(user)
        return render(request, "password_reset_confirm.html", {"form": form})
    else:
        messages.error(request, "Link expired")
    messages.error(request, "Something went wrong")
    return redirect("home")


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
