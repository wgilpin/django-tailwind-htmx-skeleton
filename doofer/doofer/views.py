from django.shortcuts import render

from doofer.models import Note

def index(request):
    context = {
        "title": "Django example",
    }
    if request.method == "POST":
        return render(request, "partial.html", context)
    notes = Note.objects.all()
    context["notes"] = notes
    return render(request, "index.html", context)
