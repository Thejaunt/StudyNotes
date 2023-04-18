from django.contrib.auth import logout, login, get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from accounts.froms import PassResetForm, PasswordSetForm, CustomUserCreationForm, CustomUserLoginForm, \
    ProfileUsernameForm, ProfileImageForm
from accounts.models import CustomUser
from accounts.tokens import account_activation_token


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
            for error in form.errors.values():
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

        for key, error in form.errors.items():
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
                for error in form.errors.values():
                    messages.error(request, error)

        form = PasswordSetForm(user)
        return render(request, "password_reset_confirm.html", {"form": form})
    else:
        messages.error(request, "Link expired")
    messages.error(request, "Something went wrong")
    return redirect("home")


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
            for key, error in form.errors.items():
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
            for key, error in form.errors.items():
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
