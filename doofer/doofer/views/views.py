from django.forms import ModelForm
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

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ["title", "comment", "snippet", "url"]


def note_edit(request, id):
    note = Note.objects.get(pk=id)
    form = NoteForm(instance=note)
    context = {"form": form}
    if request.method == "POST":
        title = request.POST.get("title")
        comment = request.POST.get("comment")
        snippet = request.POST.get("snippet")
        url = request.POST.get("url")
        note.title = title
        note.comment = comment
        note.snippet = snippet
        note.url = url
        # convert html to markdown
        note.full_clean()
        note.save()
        return redirect("note_details", id=id)

    return render(request, "notes/note_edit.html", context)