""" Django view methods """

# pylint: disable=no-member

from django.forms import ModelForm
from django.shortcuts import redirect, render

from doofer.models import Note
from doofer.search import do_text_search


def index(request):
    """Home page view"""
    context = {
        "title": "Doofer",
    }
    if request.method == "POST":
        return render(request, "partial.html", context)
    # set notes to all notes belonging to the current user
    notes = Note.objects.filter(user=request.user.pk)
    context["notes"] = notes
    return render(request, "notes/note_list.html", context)


def note_details(request, id_):
    """Note details partial view"""
    note = Note.objects.get(pk=id_)
    context = {
        "title": note.title,
        "note": note,
    }
    return render(request, "notes/note_details.html", context)


class NoteForm(ModelForm):
    """Form for editing a note"""

    class Meta:
        """form fields"""

        model = Note
        fields = ["title", "comment", "url"]


def note_edit(request, id_):
    """Edit a note"""
    note = Note.objects.get(pk=id_)

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
    """endpoint for the search"""
    if request.method != "POST":
        raise ValueError("Invalid request method")
    print("search endpoint")
    query = request.POST.get("search")
    if not query:
        return redirect("index")
    # case insensitive search
    notes = do_text_search(query, uid=request.user.pk)
    context = {
        "title": "Search results",
        "notes": notes,
        "search_term": query,
    }
    payload = render(request, "notes/note_list.html", context)
    print("rendered search results")
    return payload
