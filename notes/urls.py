from django.urls import path
from .views import home, register, user_login, user_logout, create_note_view, view_notes, view_all_public_notes,\
    note_detail_view, update_note


urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("create_note/", create_note_view, name="create_note"),
    path("view_notes/", view_notes, name="view_notes"),
    path("view_all_public_notes/", view_all_public_notes, name="public_notes"),
    path("detail_view/<int:pk>/", note_detail_view, name='detail_view'),
    path("update_note/<int:pk>/", update_note, name="update_note"),
]

