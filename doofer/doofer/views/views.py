from django.shortcuts import render, redirect

from doofer.models import Note


def index(request):
    context = {
        "title": "Django example",
    }
    if request.method == "POST":
        return render(request, "partial.html", context)
    notes = Note.objects.all()
    context["notes"] = notes
    return render(request, "notes/note_list.html", context)
