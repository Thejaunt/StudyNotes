from django.urls import path
from .views import home, create_note_view, view_personal_notes,\
    view_all_public_notes, personal_note_detail_view, update_note, delete_note_view, public_note_detail_view,\
    profile_view, like_view


urlpatterns = [
    path("", home, name="home"),

    path("create_note/", create_note_view, name="create_note"),
    path("delete_note/<int:pk>", delete_note_view, name="delete_note"),
    path("update_note/<int:pk>/", update_note, name="update_note"),
    path("personal_notes/", view_personal_notes, name="view_notes"),
    path("personal_notes/detail_view/<int:pk>/", personal_note_detail_view, name="personal_detail_view"),
    path("public_notes/", view_all_public_notes, name="public_notes"),
    path("public_notes/detail_view/<int:pk>/", public_note_detail_view, name="public_detail_view"),
    path("profile", profile_view, name="profile"),

    path("like", like_view, name="like_note"),


]

