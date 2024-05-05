from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from doofer.models import Note, User

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "password"]

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid username or password")
        return cleaned_data


def index(request):
    context = {
        "title": "Django example",
    }
    if request.method == "POST":
        return render(request, "partial.html", context)
    notes = Note.objects.all()
    context["notes"] = notes
    return render(request, "index.html", context)

def login_user(request):
    form = LoginForm()
    context = {"form": form}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    return redirect("/")