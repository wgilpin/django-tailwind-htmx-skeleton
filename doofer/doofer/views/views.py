from django.shortcuts import render, redirect

from doofer.models import Note


def index(request):
    context = {
        "title": "Django example",
    }
    if request.method == "POST":
        return render(request, "partial.html", context)
    # set notes to all notes belonging to the current user
    notes = Note.objects.filter(user=request.user.pk)
    context["notes"] = notes
    return render(request, "notes/note_list.html", context)

def note_details(request, id):
    note = Note.objects.get(pk=id)
    context = {
        "title": note.title,
        "note": note,
    }
    return render(request, "notes/note_details.html", context)