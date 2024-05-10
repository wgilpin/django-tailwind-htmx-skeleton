import csv
from datetime import datetime
import io
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from doofer.models import Note
from markdownify import markdownify


# column IDs for backup CSV upload
BACKUP_ID = 0	
BACKUP_TITLE = 1	
BACKUP_COMMENT	= 2
BACKUP_SNIPPET	= 3 
BACKUP_URL	= 4 
BACKUP_CREATED = 5


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid username or password")
        return cleaned_data


def login_user(request):
    form = LoginForm()
    context = {"form": form}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("User logged in")
            return redirect("/")
        print("User not logged in")
        messages.error(request, "Invalid username or password")
    return render(request, "auth/login.html", context)



def register_user(request):
    form = LoginForm()
    context = {"form": form}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        # does the user already exists?
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists")
            print("User already exists")
            return render(request, "auth/register.html", context)   
        # create the user
        if password == password2:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            login(request, user)
            print("User created")
            return redirect("/")
        else:
            print("Passwords do not match")
            messages.error(request, "Passwords do not match")
        print("User not created")
    return render(request, "auth/register.html", context)

def logout_user(request):
    logout(request)
    print("User logged out")
    return redirect("/")

class UploadFileForm(forms.Form):
    backup_file = forms.FileField()

def profile(request):
    message = ""
    if request.user.is_authenticated and request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            success_count, lines_count = handle_uploaded_file(request)
            message = f"{success_count} out of {lines_count} items imported"
        else:
            message = "Error processing file"
    else:
        form = UploadFileForm()
    return render(request, "auth/profile.html", {"form": form, "message": message})

def handle_uploaded_file(request):
    # https://simathapa111.medium.com/how-to-upload-a-csv-file-in-django-3a0d6295f624
    f = request.FILES["backup_file"]
    # let's check if it is a csv file
    if not f.name.endswith('.csv'):
        return 'THIS IS NOT A CSV FILE'
    data_set = f.read().decode('UTF-8')

    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)

    # skip the titles
    next(io_string)

    lines_count = 0
    success_count = 0
    # loop through each line and create a note
    for column in csv.reader(io_string, delimiter=',', quotechar='"'):
        lines_count += 1
        try:
            note: Note = Note()
            note.title = column[BACKUP_TITLE]

            # html comments convert into markdown
            comment = column[BACKUP_COMMENT]
            if column[BACKUP_SNIPPET]:
                comment += "From page:"
                comment += "<br/>"
                comment += column[BACKUP_SNIPPET]
            comment = markdownify(comment)
            note.comment = comment

            note.url = column[BACKUP_URL]
            # convert string of format '16/06/2023  18:14:17' to datetime
            if len(column[BACKUP_CREATED]) > 5:
                # ignore "null" or '' values
                created = datetime.strptime(column[BACKUP_CREATED], '%Y-%m-%d  %H:%M:%S.%f')
                note.created_at = created

            user_id = request.user.pk
            note.user = user_id
            note.save()
            print(f'Note {note.title} imported')
            success_count += 1
        except (ValueError, IndexError) as e:
            if len(column) < 6:
                print('Error: missing columns')
            else:
                print(f'Error importing {column[BACKUP_TITLE]}')
    print( f'Imported {success_count} out of {lines_count} items')
    return success_count, lines_count

