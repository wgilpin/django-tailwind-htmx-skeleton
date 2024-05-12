from django.forms import ModelForm
from django.shortcuts import render

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
        fields = ["title", "comment", "url"]


def note_edit(request, id):
    note = Note.objects.get(pk=id)

    if request.method == "POST":
        title = request.POST.get("title")
        comment = request.POST.get("comment")
        url = request.POST.get("url")
        note.title = title
        note.comment = comment
        note.url = url
        # convert html to markdown
        note.full_clean()
        note.save()
        return render(request, "notes/note_details.html", {"note": note})
    form = NoteForm(instance=note)
    context = {"form": form}
    return render(request, "notes/note_edit.html", context)


def search(request):
    query = request.GET.get("query")
    # case insensitive search
    notes = Note.objects.filter(title__icontains=query)
    context = {
        "title": "Search results",
        "notes": notes,
    }
    return render(request, "notes/note_list.html", context)
