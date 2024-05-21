from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_notes),
    path("note/<int:id_>/", views.note_detail),
    path("note/new/", views.note_create),
]
