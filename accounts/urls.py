from django.urls import path

from accounts.views import register, user_login, user_logout, activate, password_change, password_reset_request, \
    password_reset_confirm, update_profile_img, update_profile_name


urlpatterns = [
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("activate/<uidb64>/<token>", activate, name="activate"),
    path("password_change", password_change, name="password_change"),
    path("password_reset", password_reset_request, name="password_reset"),
    path("reset/<uidb64>/<token>", password_reset_confirm, name="password_reset_confirm"),
    path("profile/update_profile_img", update_profile_img, name="profile_img_update"),
    path("profile/update_profile_name", update_profile_name, name="profile_name_update"),
    ]
